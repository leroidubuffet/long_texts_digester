import os
from openai import OpenAI

def read_config(config_path):
    """Reads the OpenAI API key from the configuration file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            print(f"Reading config file: {config_path}")
            for line in file:
                if line.startswith("OPENAI_API_KEY"):
                    print("OpenAI API key found in config file.")
                    return line.split('=')[1].strip()
        print(f"Error: 'OPENAI_API_KEY' not found in '{config_path}'.")
        return None
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the config file: {e}")
        return None

def list_models():
    # Read the OpenAI API key from the config file
    config_path = os.path.join(os.path.dirname(__file__), '.config', 'config')
    openai_api_key = read_config(config_path)
    if openai_api_key is None:
        return None

    # Set up OpenAI API key
    client = OpenAI(api_key=openai_api_key)

    try:
        print("Fetching available models from OpenAI API...")
        models = client.models.list()
        print("Available models:")
        for model in models.data:
            print(f"ID: {model.id}, Created: {model.created}, Owned by: {model.owned_by}")
    except Exception as e:
        print(f"An error occurred while fetching the models: {e}")

if __name__ == "__main__":
    list_models()