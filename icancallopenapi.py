import argparse
from typing import Any

from langchain import PromptTemplate, LLMMathChain, WikipediaAPIWrapper, GoogleSearchAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain.chains import OpenAPIEndpointChain
from langchain.chat_models import ChatOpenAI
from langchain.requests import Requests
from langchain.tools import OpenAPISpec, APIOperation, Tool

from formosa_foundation_model import FormosaFoundationModel

parser = argparse.ArgumentParser(description="Call Central Weather Bureau Open API from langchain")
parser.add_argument("--api_key", type=str, required=True, help="CWB API key")
parser.add_argument("--spec_location", type=str, required=True, help="Location of CWB Open API spec")
parser.add_argument("--verbose", type=bool, action=argparse.BooleanOptionalAction, default=False,
                    help="Whether to show verbose output")
parser.add_argument("query", type=str, help="The query to ask")

parsed_args = parser.parse_args()

spec = OpenAPISpec.from_file(parsed_args.spec_location)
# print(f"Open API spec: {spec}")

# 只包裝使用這一個endpoint。每個要包裝的endpoint都會是一個tool
operation = APIOperation.from_openapi_spec(spec, "/v1/rest/datastore/F-C0032-001", "get")

# llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0)
llm = FormosaFoundationModel(temperature=0.01, max_new_tokens=1024)


class RequestsWithAuthHeader(Requests):
    """中央氣象局的API需要加上Authorization header。用這個物件包裝Requests加上需要的header"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = {"Authorization": parsed_args.api_key}


def patch(clazz, name, replacement):
    def wrap_original(orig):
        # when called with the original function, a new function will be returned
        # this new function, the wrapper, replaces the original function in the class
        # and when called it will call the provided replacement function with the
        # original function as first argument and the remaining arguments filled in by Python

        def wrapper(*args, **kwargs):
            return replacement(orig, *args, **kwargs)

        return wrapper

    orig = getattr(clazz, name)
    setattr(clazz, name, wrap_original(orig))


def replacement_function(orig, self, **kwargs: Any):
    # orig here is the original function, so can be called like this:
    # orig(self, ... args ...)
    if 'template' in kwargs:
        kwargs['template'] = "#zh-tw\n" + kwargs['template']
    orig(self, **kwargs)


# Monkey patch PromptTemplate to always get Chinese results
# https://stackoverflow.com/q/37103476
patch(PromptTemplate, '__init__', replacement_function)

weather_chain = OpenAPIEndpointChain.from_api_operation(
    operation,
    llm,
    requests=RequestsWithAuthHeader(),
    verbose=parsed_args.verbose,
    return_intermediate_steps=True,  # Return request and response text
)

llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=parsed_args.verbose)
wikipedia = WikipediaAPIWrapper(lang="zh")
search = GoogleSearchAPIWrapper()

tools = [
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math"
    ),
    Tool(
        name="CWB-Weather",
        func=lambda x: weather_chain(x),
        description="useful for when you need to answer questions about the weather"
    ),
    # Tool(
    #     name="Wikipedia",
    #     func=wikipedia.run,
    #     description="useful for when you need to answer questions about facts"
    # ),
    # Tool(
    #     name="GoogleSearch",
    #     description="useful for when you need to search the web to answer questions about facts",
    #     func=search.run,
    # )
]

# 用OpenAI Functions agent
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=parsed_args.verbose)

output = agent.run(parsed_args.query)

print(f"output: {output}")
