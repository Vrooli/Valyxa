import json
import logging
import os
from time import sleep
from typing import Any, Dict, Optional

import openai
import redis
import requests
import yaml
from flask import Flask, abort, jsonify, request

from src.utils.file_utils import file_path, load_yml

models = ['gpt-4', 'gpt-3.5-turbo']

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Configure openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to Redis
r = redis.Redis(host='redis', port=6379, db=0,
                decode_responses=True, password=os.environ.get('REDIS_PASS'))

# Initialize Flask
app = Flask(__name__)


@app.before_request
def limit_request_rate():
    # Read the API key from the request headers
    api_key = request.headers.get('API_KEY')

    # If no API key is provided, throw an error
    if api_key is None:
        abort(403, "API Key is required")

    # Check if API key matches with the environment variable
    expected_api_key = os.environ.get('API_FOR_VROOLI')

    # Bypass rate limit check if the key matches 'API_FOR_VROOLI'
    if api_key == expected_api_key:
        return

    # Check the Redis for the key
    count = r.get(api_key)

    if count is None:
        # If the key is not in the Redis, set it with a value of 1
        r.set(api_key, 1)
        # Also, set the key to expire in 24 hours (86400 seconds)
        r.expire(api_key, 86400)
    elif int(count) >= 5:
        # If the limit has been reached, inform the user
        abort(429, "API usage limit reached. Please try again in 24 hours.")
    else:
        # If the key is in the Redis and limit has not been reached, increment the value
        r.incr(api_key)


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
        raise ValueError(
            "Couldn't find 'OPENAI_API_KEY' in environment variables")
    try:
        logger.debug(
            f"Calling OpenAI API with model: {model}, prompt: {prompt}")
        completion = openai.ChatCompletion.create(
            model=model, messages=[{"role": "user", "content": prompt}])
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


@app.route('/generate', methods=['POST'])
def generate_text():
    # Read the API key and prompt from the request
    prompt = request.json.get('prompt')

    # Call the OpenAI API
    model = "gpt-4"
    response = call_openai_api(model, prompt)

    if response is not None:
        return jsonify({"response": response}), 200
    else:
        return jsonify({"error": "OpenAI API call failed"}), 500


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "healthy"}), 200


@app.route('/help', methods=['GET'])
def help():
    help_text = """
    To use this API, send a GET request to the '/test' endpoint.
    It sets and retrieves a key-value pair from Redis, then makes a call to the OpenAI API.
    For more information, check out the GitHub repository: https://github.com/Vrooli/Valyxa
    """
    return jsonify({"Help": help_text}), 200


if __name__ == "__main__":
    try:
        port = os.environ['VIRTUAL_PORT']
        if os.environ['FLASK_ENV'] == 'development':
            app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
