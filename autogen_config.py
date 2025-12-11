import os
from dotenv import load_dotenv

load_dotenv()


def get_llm_config():
    api_key = os.getenv('openai_api_key')
    api_base = os.getenv('openai_api_base')
    api_version = os.getenv('openai_api_version', '2025-01-01-preview')
    engine_name = os.getenv('openai_engine_name', 'gpt-4o')
    
    if not api_key or not api_base:
        return {
            "config_list": [],
            "temperature": 0.7,
            "cache_seed": None
        }
    
    config = {
        "config_list": [
            {
                "model": engine_name,
                "api_key": api_key,
                "base_url": api_base,
                "api_type": "azure",
                "api_version": api_version
            }
        ],
        "temperature": 0.7,
        "cache_seed": 42,
        "timeout": 120
    }
    
    return config
