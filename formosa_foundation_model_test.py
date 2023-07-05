import unittest

from langchain import LLMChain, PromptTemplate

from formosa_foundation_model import FormosaFoundationModel


class FormosaFoundationModelTest(unittest.TestCase):
    def test_basic(self):
        llm = FormosaFoundationModel()
        prompt_template = "{company}公司的{position}是誰?"

        chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(prompt_template))
        resp = chain.run(company="星宇航空", position="董事長")
        self.assertTrue("張國煒" in resp)


if __name__ == '__main__':
    unittest.main()
