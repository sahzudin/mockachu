import csv
import xml.etree.ElementTree as ET
import secrets
import zipfile
from flask import g
import ujson
import os
import pandas as pd

from ..generators.generator import GeneratorFormats

def write(data, format, zip=False):
    """Write generated data to files in various formats.
    
    Args:
        data (list): Generated data to write to file
        format (GeneratorFormats): Output format (JSON, XML, CSV)
        zip (bool): Whether to compress the output file
        
    Returns:
        str: Filename of the created file (with .zip extension if compressed)
    """
    directory = "api/static"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(
        directory, __random_file_name() + "." + format.name.lower())

    match format:
        case GeneratorFormats.JSON:
            __write_json(data, file_path)
        case GeneratorFormats.XML:
            __write_xml(data, file_path)
        case GeneratorFormats.CSV:
            __write_csv(data, file_path)

    if zip:
        zip_path = str(file_path).split(".")[0] + ".zip"
        __compress_file(file_path, zip_path)
        return str(zip_path).split("/")[2]

    return str(file_path).split("/")[2]

def __write_json(data, file_path):
    with open(file_path, "w") as f:
        ujson.dump(data, f)

def __write_xml(data, file_path):
    with open(file_path, "w") as f:
        f.write("<root>\n")
        for i, dict_data in enumerate(data):
            xml_str = __dict_to_xml("data", dict_data)
            f.write(xml_str + "\n")
        f.write("</root>")

def __write_csv(data, file_path):
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

def __dict_to_xml(tag, d):
    elem = ET.Element(tag)
    for key, val in d.items():
        child = ET.Element(key)
        child.text = str(val)
        elem.append(child)
    return ET.tostring(elem, "utf-8").decode("utf-8")

def __compress_file(input_file_path, output_zip_path):
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(input_file_path)

def __random_file_name():
    return secrets.token_hex(5)
