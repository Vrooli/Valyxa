import os
import yaml
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

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
