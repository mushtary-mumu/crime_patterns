"""Utilities used in various parts of the project."""

import yaml
import os
import requests
from urllib.request import urlopen, urlretrieve
from io import BytesIO
from zipfile import ZipFile
import pandas as pd

def read_yaml(path):
    """Read a YAML file.

    Args:
        path (str or pathlib.Path): Path to file.

    Returns:
        dict: The parsed YAML file.

    """
    with open(path) as stream:
        try:
            out = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            info = (
                "The YAML file could not be loaded. Please check that the path points "
                "to a valid YAML file."
            )
            raise ValueError(info) from error
    return out

## TODO: Split function into two: download, extract
def download_file(url, dest_folder, filename):

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    # filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    f = urlretrieve(url=url, filename=file_path)
    
    return file_path

def unzip_folder(zipped_folder, extract_to):
    
    zipfile = ZipFile(zipped_folder)
    zipfile.extractall(extract_to)

    return extract_to