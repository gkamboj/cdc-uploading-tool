import os

from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from config.configuration import configs


def get_prompt_response_from_openai(information, prompt):
    if not information or not prompt:
        return None
    os.environ['OPENAI_API_KEY'] = configs['openai.key']
    summary_prompt_template = PromptTemplate(input_variables=['information'], template=prompt)
    llm = ChatOpenAI(temperature=configs['openai.temperature'], model_name=configs['openai.model'])
    chain = LLMChain(llm=llm, prompt=summary_prompt_template)
    res = chain.invoke(input={'information': information})
    return res['text']