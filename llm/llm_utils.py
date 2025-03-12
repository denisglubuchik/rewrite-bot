import json

CONFIG_FILE = 'llm_config.json'

def _load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def _save_config(config_data):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config_data, file, indent=4)

def update_assistant_in_config(new_assistant_id: str):
    config = _load_config()
    config['ASSISTANT_ID'] = new_assistant_id
    _save_config(config)
