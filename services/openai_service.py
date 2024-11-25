import openai
from config.configuration import configs


def get_prompt_response(prompt, system_prompt_message):
    client = openai.OpenAI(
        api_key=configs['openai.key'],
    )
    return get_prompt_response_2(configs['openai.model'], client.chat.completions, prompt, system_prompt_message)


def get_prompt_response_2(model, client, prompt, system_prompt_message):
    if not system_prompt_message:
        system_prompt_message = 'You are a helpful assistant'
    response = client.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt_message},
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=configs['openai.maxTokens'],
        temperature=configs['openai.temperature'],
        n=1,
        stop=None,
    )
    print(response)
    return response

