"""
Valyxa AI Assistant Server

This script serves as the main server for the Valyxa AI Assistant, which powers AI features for 
the Vrooli platform. The server is built on Flask and connects to both Redis for rate limiting 
and OpenAI for generating text.

The server provides several endpoints:

- `/generate`: Accepts a POST request containing a JSON object with a 'prompt' key. The server 
then passes this prompt to OpenAI to generate a response.

- `/healthcheck`: Returns a JSON object indicating the status of the server.

- `/help`: Provides basic help information about the API.

The server also implements rate limiting, allowing each API key to make a certain number of requests 
per day. Special API keys can bypass this limit.

The `call_openai_api` function is a utility for making requests to the OpenAI API and logging the 
responses.

This script expects the following environment variables:
- 'OPENAI_API_KEY': The API key for OpenAI.
- 'API_FOR_VROOLI': The special API key that can bypass rate limits.
- 'REDIS_PASS': The password for the Redis server (if required).
- 'VIRTUAL_PORT': The port to run the server on.
- 'FLASK_ENV': The environment Flask is running in.

In the case of a critical error, such as failure to connect to Redis or OpenAI, the script logs the 
error and may terminate.
"""
import json
import logging
import os
from time import sleep
from typing import Any, Dict, Optional

import openai
import redis
import requests
from flask import Flask, abort, jsonify, request
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_jwt_extended.exceptions import (InvalidHeaderError,
                                           NoAuthorizationError,
                                           RevokedTokenError, WrongTokenError)
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

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

# Initialize JWT
jwt = JWTManager(app)
with open(file_path('../jwt_pub.pem'), 'r') as f:
    app.config['JWT_PUBLIC_KEY'] = f.read()
app.config['JWT_ALGORITHM'] = 'RS256'


@app.before_request
@jwt_required()
def limit_request_rate():
    """
    A decorator function to limit the rate of API requests.

    This function reads the 'API_KEY' from the request headers. If no API key is provided, 
    it aborts the request with a 403 status. If the API key matches the 'API_FOR_VROOLI' 
    environment variable, the function bypasses the rate limit check.

    Otherwise, it checks Redis for the API key. If the key is not present in Redis, it sets 
    the key with a value of 1 and an expiry time of 24 hours. If the key is present and its 
    count has reached the limit (currently 5), it aborts the request with a 429 status. If 
    the key is present and its count is below the limit, it increments the count.
    """
    # Read the API key from the request headers
    api_key = request.headers.get('API_KEY')

    # Extract the user ID from the JWT
    user_id = get_jwt_identity()

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


@app.errorhandler(NoAuthorizationError)
@app.errorhandler(InvalidHeaderError)
@app.errorhandler(WrongTokenError)
@app.errorhandler(RevokedTokenError)
@app.errorhandler(ExpiredSignatureError)
@app.errorhandler(InvalidTokenError)
def handle_jwt_errors(e):
    return jsonify({"error": "Invalid or expired token"}), 401


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
    if not api_key:
        logger.debug("Couldn't find 'OPENAI_API_KEY' in environment variables")
        raise ValueError(
            "Couldn't find 'OPENAI_API_KEY' in environment variables")
    try:
        logger.debug(
            "Calling OpenAI API with model: %s, prompt: %s", model, prompt)
        completion = openai.ChatCompletion.create(
            model=model, messages=[{"role": "user", "content": prompt}])
        logger.debug("Got completion: %s", json.dumps(completion))
        response = completion.choices[0].message.content
    except requests.exceptions.RequestException as e:
        logger.error("Request to OpenAI API failed: %s", e)
        return None
    return response


@app.route('/test', methods=['GET'])
def test():
    """
    Endpoint for testing the server.

    This function logs the start of the '/test' endpoint, sets and retrieves a 
    key-value pair in Redis, and makes a test call to the OpenAI API using the 
    contents of the start.yml file. It returns a JSON object with the response 
    from OpenAI, or an error message if the API call fails.
    """
    logger.info('Starting /test')

    key = "test_key"
    value = "Hello, Redis!"

    r.set(key, value)
    logger.info("Set key-value pair: %s - %s", key, value)

    sleep(1)

    retrieved_value = r.get(key)
    logger.info("Retrieved value for key '%s': %s", key, retrieved_value)

    prompt = json.dumps(load_yml('start', 'en'))

    model = "gpt-3.5-turbo"

    response = call_openai_api(model, prompt)
    if response is not None:
        logger.info("OpenAI API response: %s", response)
        return jsonify(response), 200
    else:
        logger.error("OpenAI API call failed")
        return jsonify({"error": "OpenAI API call failed"}), 500


@app.route('/generate', methods=['POST'])
def generate_text():
    """
    Endpoint for generating text with OpenAI.

    This function reads the 'prompt' from the request JSON. It then calls the 
    OpenAI API with the prompt and returns a JSON object containing the response. 
    If the API call fails, it returns an error message.
    """
    prompt = request.json.get('prompt')

    model = "gpt-3.5-turbo"
    response = call_openai_api(model, prompt)

    if response is not None:
        return jsonify({"response": response}), 200
    else:
        return jsonify({"error": "OpenAI API call failed"}), 500


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """
    Endpoint for checking the health of the server.

    This function returns a JSON object with a status of "healthy".
    """
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
        logger.error("Error starting server: %s", e)
