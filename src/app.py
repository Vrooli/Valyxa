import os
from typing import Optional, Dict, Any
import redis
import gettext
from time import sleep
import logging
import requests
import json
from flask import Flask, jsonify
import yaml
import openai

models = ['gpt-4', 'gpt-3.5-turbo']

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Configure openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to Redis
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True, password=os.environ.get('REDIS_PASS'))

app = Flask(__name__)

def file_path(filename):
    """
    Returns the absolute path to a file.

    Args:
        filename (str): Name of the file, or path relative to this file (src/app.py).

    Returns:
        str: Absolute path to the file.
    """
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the absolute path of the file
    abs_file_path = os.path.join(script_dir, filename)
    return abs_file_path

def load_yml(filename: str, lang: str) -> Optional[dict]:
    """
    Loads a YAML file based on language.

    Args:
        filename (str): Name of the file with or without '.yml' extension.
        lang (str): Language code of the YAML file. If not found, defaults to 'en'.

    Returns:
        Optional[dict]: Parsed YAML data, or None if an error occurred.
    """
    # Remove '.yml' from filename if it exists
    if filename.endswith('.yml'):
        filename = filename[:-4]

    # construct the file path
    path = f"tasks/{lang}/{filename}.yml"

    # if the specified language file does not exist, default to English
    if not os.path.exists(file_path(path)):
        logger.warning(f"Could not find file: {path}. Defaulting to English.")
        path = f"tasks/en/{filename}.yml"

    with open(file_path(path), 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logger.error(f"Error reading YAML file: {e}")
            return None

def call_openai_api(model: str, prompt: str) -> Optional[Dict[str, Any]]:
    """
    Makes a request to the OpenAI API with the provided parameters.

    Args:
        model (str): Model to use for the request.
        prompt (str): Prompt to use for the request.

    Returns:
        dict: Response from the OpenAI API or None if there was an error.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    logger.debug(f"Got key: {api_key}")
    if not api_key:
        logger.debug("Couldn't find 'OPENAI_API_KEY' in environment variables")
        raise ValueError("Couldn't find 'OPENAI_API_KEY' in environment variables")
    try:
        logger.debug(f"Calling OpenAI API with model: {model}, prompt: {prompt}")
        completion = openai.ChatCompletion.create(model=model, messages=[{"role": "user", "content": prompt}])
        logger.debug(f"Got completion: {json.dumps(completion)}")
        response = completion.choices[0].message.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to OpenAI API failed: {e}")
        return None
    return response

@app.route('/test', methods=['GET'])
def main():
    logger.info('Starting /test')

    key = "test_key"
    value = "Hello, Redis!"

    r.set(key, value)
    logger.info(f"Set key-value pair: {key} - {value}")

    sleep(1)

    retrieved_value = r.get(key)
    logger.info(f"Retrieved value for key '{key}': {retrieved_value}")

    # Load the contents of the start.yml file
    prompt = json.dumps(load_yml('start', 'en'))

    # Test call to OpenAI API function
    model = "gpt-4"

    response = call_openai_api(model, prompt)
    if response is not None:
        logger.info(f"OpenAI API response: {response}")
        return jsonify(response), 200
    else:
        logger.error("OpenAI API call failed")
        return jsonify({"error": "OpenAI API call failed"}), 500
    
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "healthy"}), 200


@app.route('/help', methods=['GET'])
def help():
    help_text = """
    To use this API, send a GET request to the '/test' endpoint.
    It sets and retrieves a key-value pair from Redis, then makes a call to the OpenAI API.
    For more information, check out the GitHub repository: https://github.com/YourUsername/YourRepo
    """
    return jsonify({"Help": help_text}), 200


if __name__ == "__main__":
    try:
        port = os.environ['VIRTUAL_PORT']
        if os.environ['FLASK_ENV'] == 'development':
            app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting server: {e}")