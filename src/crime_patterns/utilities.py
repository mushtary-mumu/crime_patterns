"""Utilities used in various parts of the project."""

import os
import pickle
from urllib.request import urlretrieve
from zipfile import ZipFile

import yaml


def read_yaml(path):
    """Read a YAML file and return the contents as a dictionary.

    Parameters:
    -----------
    path: str
        The path to the YAML file.

    Returns:
    --------
    out: dict
        The contents of the YAML file as a dictionary.

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


def download_file(url, dest_folder, filename):
    """Function to download a file from a URL.

    Parameters:
    -----------
    url: str
        The URL to download the file from.
    dest_folder: str
        The path to the folder where the file should be saved.
    filename: str
        The name of the file.

    Returns:
    --------
    file_path: str
        The path to the downloaded file.

    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    file_path = os.path.join(dest_folder, filename)

    urlretrieve(url=url, filename=file_path)

    return file_path


def unzip_folder(zip_file, output_dir, subset=False, startswith=None):
    """Function to unzip a folder.

    Parameters:
    -----------
    zip_file: str
        The path to the zip file.
    output_dir: str
        The path to the folder where the zip file should be unzipped.
    subset: bool
        Whether to unzip only a subset of the files in the zip file.
    startswith: str
        The string that the files to be unzipped should start with.

    Returns:
    --------
    output_dir: str
        The path to the folder where the zip file was unzipped.

    """
    unzipped_folder = os.path.basename(zip_file).strip(".zip")
    output_dir = os.path.join(output_dir, unzipped_folder)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    with ZipFile(zip_file) as zip_archive:

        if subset:
            for file in zip_archive.namelist():
                if file.startswith(startswith):
                    zip_archive.extract(file, output_dir)
        else:

            zip_archive.extractall(output_dir)

    return output_dir


def save_object_to_pickle(obj, output):
    """Function to save an object to a pickle file.

    Parameters:
    -----------
    obj: object
        The object to be saved.
    output: str
        The path to the pickle file.

    Returns:
    --------
    output: str
        The path to the pickle file.

    """
    with open(output, "wb") as f:
        pickle.dump(obj, f)

    return output


def load_object_from_pickle(source):
    """Function to load an object from a pickle file.

    Parameters:
    -----------
    source: str
        The path to the pickle file.

    Returns:
    --------
    obj: object
        The object loaded from the pickle file.

    """
    with open(source, "rb") as f:
        obj = pickle.load(f)

    return obj
