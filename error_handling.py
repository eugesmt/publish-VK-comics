import requests


class FileSavingError(Exception):
    pass


class VKResponse:
    def __init__(self, action, respose):
        self.action = action
        self.response = respose

    def handle_vk_api_response(self):
        actions = ['GetWallUploadServer', 'SaveWallPhoto', 'WallPost']
        if self.action in actions:
            try:
                negative_response = self.response['error']
                if negative_response:
                    raise requests.RequestException(
                        negative_response['error_msg']
                    )
            except KeyError:
                positive_response = self.response['response']
                if positive_response:
                    pass
        elif self.action == 'UploadToVKServer':
            photo = self.response['photo']
            if photo == '[]':
                raise requests.RequestException("Картинка не загружена")
            else:
                pass
