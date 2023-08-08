import requests


def handle_vk_api_response(vk_api_response_result):
    if vk_api_response_result.get('error'):
        error_code = vk_api_response_result['error']['error_code']
        error_message = vk_api_response_result['error']['error_msg']
        raise requests.RequestException(f"{error_code} {error_message}")


def handle_upload_vk_server_response(vk_api_response_result):
    if vk_api_response_result.get('photo'):
        if vk_api_response_result['photo'] == '[]':
            raise requests.RequestException("Картинка не загружена")
