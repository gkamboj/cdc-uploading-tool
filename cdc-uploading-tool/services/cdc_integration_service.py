import json
import sys
import urllib

import curlify
import requests

from config.configuration import configs
from services import cdc_config_service as ccs


def get_account_schema_from_cdc(config_id):
    cdc_config = ccs.get_cdc_config(config_id)
    url = cdc_config['url'] + '/accounts.getSchema'
    payload = {key: value for key, value in cdc_config.items() if key != 'url'}
    response = requests.post(url, data=payload)
    result = response.json()
    # print('Get Schema API response:', json.dumps(result, indent=4))
    return result


def update_template_request(payload, data):
    payload['httpStatusCodes'] = True
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = json.dumps(value)
    payload.update(data)


def send_data_to_cdc(config_id, template_id, data):
    cdc_config = ccs.get_cdc_config(config_id)
    template_endpoint = next(template['url'] for template in configs['cdc.templates'] if template['key'] == template_id)
    url = cdc_config['url'] + template_endpoint
    payload = {key: value for key, value in cdc_config.items() if key != 'url'}
    update_template_request(payload, data)
    print(f'URL is {url} and payload is {json.dumps(payload, indent=4)}')
    response = requests.post(url, data=payload)
    print('cURL is ' + curlify.to_curl(response.request))
    result = response.json()
    print('Send Data API response: ', json.dumps(result, indent=4))
    return result


def create_template_specific_request(data, template_id):
    cases = {}
    for template in configs['cdc.templates']:
        cases[template['key']] = 'create_request_' + template['key']
    method_name = cases[template_id]
    method = getattr(sys.modules[__name__], method_name)
    return method(data)


def create_request_importLiteAccount(data):
    profile_schema = 'profileSchema'
    if profile_schema in data and 'email' in data[profile_schema]:
        email_val = data[profile_schema].pop('email')
        data['email'] = email_val
        profile_schema_data = data.pop('profileSchema')
        data['profile'] = urllib.parse.quote(json.dumps(profile_schema_data))
    data['httpStatusCodes'] = True
    return data

def create_request_importFullAccount(data):
    pass
