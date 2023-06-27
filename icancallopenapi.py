import argparse

from langchain import PromptTemplate, LLMMathChain
from langchain.agents import initialize_agent, AgentType
from langchain.chains import OpenAPIEndpointChain
from langchain.chains.api.openapi.prompts import RESPONSE_TEMPLATE
from langchain.chains.api.openapi.response_chain import APIResponderOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.requests import Requests
from langchain.tools import OpenAPISpec, APIOperation, Tool

parser = argparse.ArgumentParser(description="Call Central Weather Bureau Open API from langchain")
parser.add_argument("--api_key", type=str, required=True, help="CWB API key")
parser.add_argument("--spec_location", type=str, required=True, help="Location of CWB Open API spec")
parser.add_argument("--verbose", type=bool, action=argparse.BooleanOptionalAction, default=False, help="Whether to show verbose output")
parser.add_argument("query", type=str, help="The query to ask")

parsed_args = parser.parse_args()


RESPONSE_TEMPLATE_ZH = "#zh-tw\n" + RESPONSE_TEMPLATE

spec = OpenAPISpec.from_file(parsed_args.spec_location)
# print(f"Open API spec: {spec}")

# 只包裝使用這一個endpoint。每個要包裝的endpoint都會是一個tool
operation = APIOperation.from_openapi_spec(spec, "/v1/rest/datastore/F-C0032-001", "get")

llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0)


class RequestsWithAuthHeader(Requests):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {"Authorization": parsed_args.api_key}


weather_chain = OpenAPIEndpointChain.from_api_operation(
    operation,
    llm,
    requests=RequestsWithAuthHeader(),
    verbose=parsed_args.verbose,
    return_intermediate_steps=True,  # Return request and response text
)
weather_chain.api_response_chain.prompt = PromptTemplate(
            template=RESPONSE_TEMPLATE_ZH,  # 下prompt的時候指定用中文回答
            output_parser=APIResponderOutputParser(),
            input_variables=["response", "instructions"],
        )

llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=parsed_args.verbose)
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
    )
]
agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=parsed_args.verbose)

output = agent.run(parsed_args.query)

print(f"output: {output}")
