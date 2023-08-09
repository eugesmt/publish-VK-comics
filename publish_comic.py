import os
import random

import requests
from dotenv import load_dotenv

import error_handling as err
import file_operations as fop


def fetch_xkcd_comics():
    latest_comic_url = "https://xkcd.com/info.0.json"
    response = requests.get(url=latest_comic_url)
    latest_comic = response.json()
    latest_comic_number = latest_comic['num']
    random_comic_number = random.randint(1, latest_comic_number)
    comic_url = f"https://xkcd.com/{random_comic_number}/info.0.json"
    response = requests.get(url=comic_url)
    response.raise_for_status()
    comic = response.json()
    image_url = comic["img"]
    comic_text = comic["alt"]
    file_path = fop.save_image(image_url)
    return file_path, comic_text


def get_vk_upload_url(vk_group_id, vk_access_token, vk_api_version):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "v": vk_api_version,
        "group_id": vk_group_id,
        "access_token": vk_access_token
    }
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    vk_response_result = response.json()
    err.handle_vk_api_response(vk_response_result)
    upload_url = vk_response_result['response']['upload_url']
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
    uploading_vk_server_result = response.json()
    err.handle_upload_vk_server_response(uploading_vk_server_result)
    server = uploading_vk_server_result['server']
    photo = uploading_vk_server_result['photo']
    uploading_vk_server_hash = uploading_vk_server_result['hash']
    return server, photo, uploading_vk_server_hash


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
    err.handle_upload_vk_server_response(saved_photo)
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
    photo_publishing_result = response.json()
    err.handle_upload_vk_server_response(photo_publishing_result)


def main():
    load_dotenv()
    vk_group_id = os.environ['VK_GROUP_ID']
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_api_version = os.environ['VK_API_VERSION']
    try:
        file_path, comic_text = fetch_xkcd_comics()
        server, photo, uploading_vk_server_hash = upload_to_vk_server(
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
            uploading_vk_server_hash
        )
        publish_photo_to_wall(
            vk_group_id,
            vk_access_token,
            vk_api_version,
            photo_owner_id,
            photo_id,
            comic_text
        )
    except requests.RequestException as error:
        print(error)
    finally:
        os.remove(file_path)


if __name__ == "__main__":
    main()
