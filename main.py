import requests
import os
from pathlib import Path
from urllib.parse import urlsplit
from dotenv import load_dotenv
from functions_upload_images import saved_image


# Скачиваение комикса
def fetch_xkcd():
    url = "https://xkcd.com/info.0.json"
    image_path = Path() / 'images' / 'xkcd'
    response = requests.get(url=url)
    response.raise_for_status()
    comics = response.json()
    image_url = comics["img"]
    comics_text = comics["alt"]
    image_link_path = urlsplit(image_url).path
    _, image_path_tail = os.path.split(image_link_path)
    saved_image(
        image_url,
        image_path,
        image_path_tail
    )
    file_path = Path() / image_path / image_path_tail
    return file_path, comics_text


# Получение адреса от сервера на загрузку
def get_vk_upload_url(vk_group_id, vk_access_token, vk_api_version):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "v": vk_api_version,
        "group_id": vk_group_id,
        "access_token": vk_access_token
    }
    response = requests.get(url=url, params=params)
    upload_url = response.json()['response']['upload_url']
    return upload_url


# Загрузка на сервер по адресу
def upload_to_vk_server(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        file_path
):
    with open(file_path, 'rb') as file:
        url = get_vk_upload_url(vk_group_id, vk_access_token, vk_api_version)
        files = {
            'photo': file,
        }
        params = {
            "v": vk_api_version,
            "group_id": vk_group_id,
            "access_token": vk_access_token
        }
        response = requests.post(url, files=files, params=params)
        response.raise_for_status()
        metadata = response.json()
    return metadata['server'], metadata['photo'], metadata['hash']


# Сохранение фото на сервере
def save_photo_to_vk_server(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        server,
        photo,
        hash
):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "group_id": vk_group_id,
        "server": server,
        "photo": photo,
        "hash": hash,
        "access_token": vk_access_token,
        "v": vk_api_version
    }
    response = requests.post(url=url, params=params)
    response.raise_for_status()
    data = response.json()
    owner_id = data['response'][0]['owner_id']
    photo_id = data['response'][0]['id']
    return owner_id, photo_id


# Публикация фото на стене
def publish_photo_to_wall(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        owner_id,
        photo_id,
        comics_text
):
    url = "https://api.vk.com/method/wall.post"
    params = {
        "v": vk_api_version,
        "group_id": vk_group_id,
        "access_token": vk_access_token,
        "attachments": f'photo{owner_id}_{photo_id}',
        "owner_id": -vk_group_id,
        "from_group": 1,
        "message": comics_text
    }
    response = requests.post(url=url, params=params)
    response.raise_for_status()


def main():
    load_dotenv()
    vk_group_id = os.environ['VK_GROUP_ID']
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_api_version = os.environ['VK_API_VERSION']
    file_path, comics_text = fetch_xkcd()
    server, photo, hash = upload_to_vk_server(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        file_path
    )
    owner_id, photo_id = save_photo_to_vk_server(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        server,
        photo,
        hash
    )
    publish_photo_to_wall(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        owner_id,
        photo_id,
        comics_text
    )


if __name__ == "__main__":
    main()
