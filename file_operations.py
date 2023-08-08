import os
from pathlib import Path
from urllib.parse import urlsplit

import requests


def save_image(url, image_path):
    response = requests.get(url)
    response.raise_for_status()
    image_link_path = urlsplit(url).path
    _, image_path_tail = os.path.split(image_link_path)
    Path(image_path).mkdir(parents=True, exist_ok=True)
    file_path = Path() / image_path / image_path_tail
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path
