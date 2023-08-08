import os
import shutil
from pathlib import Path
from urllib.parse import urlsplit

import requests


def create_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def delete_directory(file_path):
    head_path_tail, _ = os.path.split(file_path)
    if os.path.exists(head_path_tail):
        shutil.rmtree(head_path_tail)


def save_image(url, image_path):
    response = requests.get(url)
    response.raise_for_status()
    image_link_path = urlsplit(url).path
    _, image_path_tail = os.path.split(image_link_path)
    create_directory(image_path)
    file_path = Path() / image_path / image_path_tail
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path
