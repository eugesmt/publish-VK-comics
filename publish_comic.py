import os
import random
import shutil
from pathlib import Path
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv

import error_handling as err


def save_image(url, file_path):
    response = requests.get(url)
    if response.ok:
        with open(file_path, 'wb') as file:
            file.write(response.content)
    response.raise_for_status()


def fetch_xkcd_comics():
    image_path = Path() / 'images' / 'xkcd'
    latest_comic_url = "https://xkcd.com/info.0.json"
    response = requests.get(url=latest_comic_url)
    if response.ok:
        latest_comic = response.json()
        latest_comic_number = latest_comic['num']
        random_comic_number = random.randint(1, latest_comic_number)
        comic_url = f"https://xkcd.com/{random_comic_number}/info.0.json"
        response = requests.get(url=comic_url)
        if response.ok:
            comic = response.json()
            image_url = comic["img"]
            comic_text = comic["alt"]
            image_link_path = urlsplit(image_url).path
            _, image_path_tail = os.path.split(image_link_path)
            Path(image_path).mkdir(parents=True, exist_ok=True)
            file_path = Path() / image_path / image_path_tail
            try:
                save_image(
                    image_url,
                    file_path
                )
                return file_path, comic_text
            except requests.RequestException:
                shutil.rmtree(image_path)
                raise err.FileSavingError("Ошибка при скачивании файла")
            except OSError:
                shutil.rmtree(image_path)
                raise err.FileSavingError("Ошибка сохранения файла")
    response.raise_for_status()


def get_vk_upload_url(vk_group_id, vk_access_token, vk_api_version):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "v": vk_api_version,
        "group_id": vk_group_id,
        "access_token": vk_access_token
    }
    response = requests.get(url=url, params=params)
    if response.ok:
        action = "GetWallUploadServer"
        action_response_result = response.json()
        vk_api_response = err.VKResponse(action, action_response_result)
        vk_api_response.handle_vk_api_response()
        upload_url = response.json()['response']['upload_url']
        return upload_url
    response.raise_for_status()


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
    if response.ok:
        upload_result = response.json()
        action = "UploadToVKServer"
        vk_api_response = err.VKResponse(action, upload_result)
        vk_api_response.handle_vk_api_response()
        server = upload_result['server']
        photo = upload_result['photo']
        upload_result_hash = upload_result['hash']
        return server, photo, upload_result_hash
    response.raise_for_status()


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
    if response.ok:
        saved_photo = response.json()
        action = "SaveWallPhoto"
        vk_api_response = err.VKResponse(action, saved_photo)
        vk_api_response.handle_vk_api_response()
        photo_owner_id = saved_photo['response'][0]['owner_id']
        photo_id = saved_photo['response'][0]['id']
        return photo_owner_id, photo_id
    response.raise_for_status()


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
    response_result = response.json()
    action = "WallPost"
    vk_api_response = err.VKResponse(action, response_result)
    vk_api_response.handle_vk_api_response()
    response.raise_for_status()


def main():
    load_dotenv()
    vk_group_id = os.environ['VK_GROUP_ID']
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_api_version = os.environ['VK_API_VERSION']
    try:
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
    except requests.RequestException as error:
        print(error)
    except err.FileSavingError as error:
        print(error)
    finally:
        head_path_tail, _ = os.path.split(file_path)
        if os.path.isdir(head_path_tail):
            shutil.rmtree(head_path_tail)


if __name__ == "__main__":
    main()
