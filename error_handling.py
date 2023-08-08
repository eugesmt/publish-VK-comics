import requests


def handle_vk_api_response(response_result):
    try:
        if response_result['error']:
            error_code = response_result['error']['error_code']
            error_message = response_result['error']['error_msg']
            raise requests.RequestException(f"{error_code} {error_message}")
    except KeyError:
        pass


def handle_upload_vk_server_response(response_result):
    try:
        if response_result['photo'] == '[]':
            raise requests.RequestException("Картинка не загружена")
    except KeyError:
        pass
