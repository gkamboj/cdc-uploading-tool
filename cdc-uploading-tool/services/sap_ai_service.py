import os

from gen_ai_hub.proxy.langchain import ChatOpenAI

from config.configuration import configs
from services import openai_service as ois


def set_proxy_config():
    os.environ['AICORE_AUTH_URL'] = configs['sapAI.configs.authUrl'] + "/oauth/token"
    os.environ['AICORE_CLIENT_ID'] = configs['sapAI.configs.clientId']
    os.environ['AICORE_CLIENT_SECRET'] = configs['sapAI.configs.clientSecret']
    os.environ['AICORE_BASE_URL'] = configs['sapAI.configs.apiUrl'] + "/v2"
    os.environ['AICORE_LLM_RESOURCE_GROUP'] = configs['sapAI.configs.resourceGroup']


def get_prompt_response_from_openai(prompt, system_prompt_message):
    model = configs['sapAI.openai.model']
    llm = ChatOpenAI(proxy_model_name=model)
    return ois.get_prompt_response_2(model, llm.client, prompt, system_prompt_message)


def get_prompt_response(prompt, system_prompt_message):
    set_proxy_config()
    # Handle cases if more tenants need to be added in the future, defaulting to OpenAI for now
    return get_prompt_response_from_openai(prompt, system_prompt_message)