import os
import json

def read_resource_file(file_name):
    """Read the entire content of a resource file.
    
    Args:
        file_name (str): Name of the resource file to read
        
    Returns:
        str: The complete content of the file
    """
    current_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(current_dir, "res", file_name)

    with open(full_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_resource_file_lines(file_name):
    """Read a resource file and return non-empty lines as a list.
    
    Args:
        file_name (str): Name of the resource file to read
        
    Returns:
        list: List of non-empty, stripped lines from the file
    """
    content = read_resource_file(file_name)
    return [line.strip() for line in content.splitlines() if line.strip()]

def read_resource_file_json(file_name):
    """Read a JSON resource file and parse it into a Python object.
    
    Args:
        file_name (str): Name of the JSON resource file to read
        
    Returns:
        dict or list: Parsed JSON content
    """
    content = read_resource_file(file_name)
    return json.loads(content)

def get_resource_path(file_name):
    """Get the full path to a resource file.
    
    Args:
        file_name (str): Name of the resource file
        
    Returns:
        str: Full path to the resource file
    """
    current_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(current_dir, "res", file_name)
