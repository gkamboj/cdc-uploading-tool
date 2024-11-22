import json
import os

CDC_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'cdc_configs.json')


def load_cdc_configs():
    cdc_configs = {}
    with open(CDC_CONFIG_FILE, 'r') as f:
        data = f.read()
        if data.strip() != '':
            cdc_configs = json.loads(data)
    return cdc_configs


def get_cdc_config(config_id):
    config = {}
    cdc_configs = load_cdc_configs()
    if config_id in list(cdc_configs.keys()):
        config = cdc_configs[config_id]
    print('CDC config is {}'.format(config))
    return config


def update_cdc_config(cdc_config):
    cdc_configs = load_cdc_configs()
    cdc_configs[cdc_config['configId']] = create_cdc_config(cdc_config)
    with open(CDC_CONFIG_FILE, 'w') as f:
        json.dump(cdc_configs, f, indent=4)
    print('Updated CDC configs are {}'.format(cdc_configs))


def create_cdc_config(cdc_config):
    data = {}
    for config_key in cdc_config:
        if config_key != 'configId':
            data[config_key] = cdc_config[config_key]
    return data
