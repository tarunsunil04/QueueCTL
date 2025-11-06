# config.py
import json
import os

CONFIG_FILE = ".queuectl_config.json"

DEFAULT_CONFIG = {
    "max_retries": 5,
    "backoff_base": 3
}

def get_config():
    """Load config from file, or return defaults if not found."""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Ensure all default keys are present
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except json.JSONDecodeError:
        print(f"Warning: Config file {CONFIG_FILE} is corrupt. Using defaults.")
        return DEFAULT_CONFIG

def set_config_value(key, value):
    """Write a specific key-value pair to the config file."""
    config = get_config()
    
    if key not in DEFAULT_CONFIG:
        raise KeyError(f"Invalid config key: {key}. Valid keys are: {list(DEFAULT_CONFIG.keys())}")

    try:
        original_type = type(DEFAULT_CONFIG[key])
        value = original_type(value)
    except ValueError:
        raise ValueError(f"Invalid value type for {key}. Expected {original_type.__name__}.")

    config[key] = value
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Config updated: {key} = {value}")