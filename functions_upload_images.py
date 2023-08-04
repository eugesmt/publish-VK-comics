from pathlib import Path

import requests


def saved_image(url, image_path, image_name):
    response = requests.get(url)
    response.raise_for_status()
    Path(image_path).mkdir(parents=True, exist_ok=True)
    file_path = Path() / image_path / image_name
    with open(file_path, 'wb') as file:
        file.write(response.content)
