"""Utilities used in various parts of the project."""

import os
import pickle
from urllib.request import urlretrieve
from zipfile import ZipFile

import yaml


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


def download_file(url, dest_folder, filename):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    file_path = os.path.join(dest_folder, filename)

    urlretrieve(url=url, filename=file_path)

    return file_path


def unzip_folder(zip_file, output_dir, subset=False, startswith=None):
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
    with open(output, "wb") as f:
        pickle.dump(obj, f)

    return output


def load_object_from_pickle(source):
    with open(source, "rb") as f:
        obj = pickle.load(f)

    return obj
