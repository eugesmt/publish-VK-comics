import os
import random
from pathlib import Path
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv


def save_image(url, file_path):
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)


def fetch_xkcd_comics():
    image_path = Path() / 'images' / 'xkcd'
    latest_comic_url = "https://xkcd.com/info.0.json"
    response = requests.get(url=latest_comic_url)
    response.raise_for_status()
    latest_comic = response.json()
    latest_comic_number = latest_comic['num']
    random_comic_number = random.randint(1, latest_comic_number)
    comic_url = f"https://xkcd.com/{random_comic_number}/info.0.json"
    response = requests.get(url=comic_url)
    response.raise_for_status()
    comic = response.json()
    image_url = comic["img"]
    comic_text = comic["alt"]
    image_link_path = urlsplit(image_url).path
    _, image_path_tail = os.path.split(image_link_path)
    Path(image_path).mkdir(parents=True, exist_ok=True)
    file_path = Path() / image_path / image_path_tail
    save_image(
        image_url,
        file_path
    )
    return file_path, comic_text


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
        upload_result = response.json()
        server = upload_result['server']
        photo = upload_result['photo']
        upload_result_hash = upload_result['hash']
    return server, photo, upload_result_hash


def save_photo_to_vk_server(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        server,
        photo,
        upload_result_hash
):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "group_id": vk_group_id,
        "server": server,
        "photo": photo,
        "hash": upload_result_hash,
        "access_token": vk_access_token,
        "v": vk_api_version
    }
    response = requests.post(url=url, params=params)
    response.raise_for_status()
    saved_photo = response.json()
    photo_owner_id = saved_photo['response'][0]['owner_id']
    photo_id = saved_photo['response'][0]['id']
    return photo_owner_id, photo_id


def publish_photo_to_wall(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        photo_owner_id,
        photo_id,
        comic_text
):
    url = "https://api.vk.com/method/wall.post"
    params = {
        "v": vk_api_version,
        "group_id": vk_group_id,
        "access_token": vk_access_token,
        "attachments": f'photo{photo_owner_id}_{photo_id}',
        "owner_id": f"-{vk_group_id}",
        "from_group": 1,
        "message": comic_text
    }
    response = requests.post(url=url, params=params)
    response.raise_for_status()


def main():
    load_dotenv()
    vk_group_id = os.environ['VK_GROUP_ID']
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_api_version = os.environ['VK_API_VERSION']
    file_path, comic_text = fetch_xkcd_comics()
    server, photo, upload_result_hash = upload_to_vk_server(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        file_path
    )
    photo_owner_id, photo_id = save_photo_to_vk_server(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        server,
        photo,
        upload_result_hash
    )
    publish_photo_to_wall(
        vk_group_id,
        vk_access_token,
        vk_api_version,
        photo_owner_id,
        photo_id,
        comic_text
    )
    os.remove(file_path)


if __name__ == "__main__":
    main()
