import os
import time
import logging
from datetime import datetime
from openai import OpenAI
from tiktoken import encoding_for_model
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_file(file_path):
    """Reads the contents of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            logging.info(f"Reading file: {file_path}")
            return file.read()
    except FileNotFoundError:
        logging.error(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        logging.error(f"An error occurred while reading the file: {e}")
        return None

def read_config(config_path):
    """Reads the OpenAI API key from the configuration file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            logging.info(f"Reading config file: {config_path}")
            for line in file:
                if line.startswith("OPENAI_API_KEY"):
                    logging.info("OpenAI API key found in config file.")
                    return line.split('=')[1].strip()
        logging.error(f"Error: 'OPENAI_API_KEY' not found in '{config_path}'.")
        return None
    except FileNotFoundError:
        logging.error(f"Error: Config file '{config_path}' not found.")
        return None
    except Exception as e:
        logging.error(f"An error occurred while reading the config file: {e}")
        return None

def send_large_text_to_chatgpt(file_path, prompt=None, model="chatgpt-4o-latest"):
    # Read the file contents
    text_data = read_file(file_path)
    if text_data is None:
        return None, None, None, None, None

    # Read the OpenAI API key from the config file
    config_path = os.path.join(os.path.dirname(__file__), '.config', 'config')
    openai_api_key = read_config(config_path)
    if openai_api_key is None:
        return None, None, None, None, None

    # Set up OpenAI API key
    client = OpenAI(api_key=openai_api_key)

    # Initialize tokenizer
    logging.info("Initializing tokenizer...")
    tokenizer = encoding_for_model(model)

    # Encode text data into token integers
    logging.info("Encoding text data into tokens...")
    token_integers = tokenizer.encode(text_data)

    # Split token integers into chunks
    max_tokens = 4000  # Adjust based on the chosen model
    chunk_size = max_tokens - len(tokenizer.encode(prompt)) if prompt else max_tokens
    chunks = [
        token_integers[i:i+chunk_size]
        for i in range(0, len(token_integers), chunk_size)
    ]

    # Decode token chunks back to strings
    logging.info("Decoding token chunks back to strings...")
    chunks = [tokenizer.decode(chunk) for chunk in chunks]

    messages = []
    if prompt:
        messages.append({"role": "user", "content": prompt})
    messages.append({
        "role": "user",
        "content": "To provide the context for the above prompt, I will send you text in parts. When I am finished, I will tell you 'ALL PARTS SENT'. Do not answer until you have received all the parts."
    })

    for i, chunk in enumerate(chunks):
        logging.info(f"Sending part {i+1} to ChatGPT...")
        messages.append({"role": "user", "content": f"Part {i+1}:\n{chunk}"})

    messages.append({"role": "user", "content": "ALL PARTS SENT"})

    try:
        logging.info("Sending request to OpenAI API...")
        start_time = time.time()
        response = client.chat.completions.create(model=model, messages=messages)
        end_time = time.time()
        logging.info("Received response from OpenAI API.")

        total_tokens_sent = sum(len(tokenizer.encode(chunk)) for chunk in chunks)
        total_tokens_generated = len(tokenizer.encode(response.choices[0].message.content.strip()))
        total_tokens_received = total_tokens_sent + total_tokens_generated
        total_time_taken = end_time - start_time

        return response.choices[0].message.content.strip(), total_tokens_sent, total_tokens_generated, total_tokens_received, total_time_taken
    except Exception as e:
        logging.error(f"An error occurred while processing the request: {e}")
        return None, None, None, None, None

def write_to_file(file_path, content, header):
    """Writes the given content to a file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(header + "\n\n" + content)
        logging.info(f"Response saved to file: {file_path}")
    except Exception as e:
        logging.error(f"An error occurred while writing to the file: {e}")

def main():
    logging.info("Starting the script...")
    logging.info(f"Current working directory: {os.getcwd()}")

    # Prompt the user for the input file path
    file_path = prompt("Please enter the path to the input text file: ", completer=PathCompleter()).strip()
    if not os.path.isfile(file_path):
        logging.error(f"Error: The file '{file_path}' does not exist.")
        exit(1)

    # Prompt the user for the prompt file path
    prompt_path = prompt("Please enter the path to the prompt file: ", completer=PathCompleter()).strip()
    if not os.path.isfile(prompt_path):
        logging.error(f"Error: The file '{prompt_path}' does not exist.")
        exit(1)

    # Prompt the user for the output file path
    output_file_path = prompt("Please enter the path to the output file: ", completer=PathCompleter()).strip()

    # Read the prompt from a file
    prompt_text = read_file(prompt_path)
    if prompt_text is None:
        logging.error("Failed to read the prompt file.")
    else:
        result, total_tokens_sent, total_tokens_generated, total_tokens_received, total_time_taken = send_large_text_to_chatgpt(file_path, prompt=prompt_text)
        if result:
            # Create the header
            header = (
                f"Date of Generation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Model Used: chatgpt-4o-latest\n"
                f"Total Tokens Sent: {total_tokens_sent}\n"
                f"Total Tokens Generated: {total_tokens_generated}\n"
                f"Total Tokens Received: {total_tokens_received}\n"
                f"Total Time Taken: {total_time_taken:.2f} seconds\n"
                f"Input File Path: {file_path}\n"
                f"Prompt File Path: {prompt_path}"
            )
            write_to_file(output_file_path, result, header)
        else:
            logging.error("Failed to process the file.")
    logging.info("Script finished.")

if __name__ == "__main__":
    main()
