#!/bin/env python3

import base64
import io
import json
import tempfile
from typing import Tuple, Dict, Any

import requests
from PIL import Image

from configs import ConfigBuilder


class TelegramBot:
    def __init__(self, config=None):
        self.config = config
        self.token = self.config.telegram_setting.bot_token
        self.chat_id = self.config.telegram_setting.chat_id

        self.urls = {
            'text': f'https://api.telegram.org/bot{self.token}/sendMessage',
            'doc': f'https://api.telegram.org/bot{self.token}/sendDocument',
            'edit_message_media': f'https://api.telegram.org/bot{self.token}/editMessageMedia',
            'pic': f'https://api.telegram.org/bot{self.token}/sendPhoto',
            'pin_message': f'https://api.telegram.org/bot{self.token}/pinChatMessage',
            'unpin_message': f'https://api.telegram.org/bot{self.token}/unpinChatMessage',
            'unpin_all_messages': f'https://api.telegram.org/bot{self.token}/unpinAllChatMessages',
        }

    def send_text_message(self, message) -> Tuple[str, Dict[str, Any]]:
        payload = {'chat_id': self.chat_id, 'text': message, 'parse_mode': 'html'}
        send_text_message_response = requests.post(self.urls['text'], data=payload)
        response_json = json.loads(send_text_message_response.text)

        if response_json['ok']:
            info_dict = {
                'chat_id': str(response_json['result']['chat']['id']),
                'message_id': str(response_json['result']['message_id'])
            }
            return 'OK', info_dict
        else:
            response_json.pop('ok')
            return 'ERROR', response_json

    def send_image_message(self, base64_encoded_image,
                           filename: str = '',
                           caption: str = '',
                           as_document: bool = True) -> Tuple[str, Dict[str, Any]]:
        file_content = base64.b64decode(base64_encoded_image)

        with tempfile.TemporaryFile() as f, tempfile.TemporaryFile() as thumb_f:

            f.write(file_content)
            f.seek(0)

            stream = io.BytesIO(file_content)
            img = Image.open(stream).resize((320, 214))
            img.save(thumb_f, "JPEG")
            thumb_f.seek(0)

            if as_document:
                payload = {'chat_id': self.chat_id, 'thumb': 'attach://preview_' + filename,
                           'caption': caption}
                files = {'document': (filename, f, 'image/jpeg'),
                         'thumb': ('preview_' + filename, thumb_f, 'image/jpeg')}

                send_image_response = requests.post(self.urls['doc'], data=payload, files=files)
            else:
                payload = {'chat_id': self.chat_id, 'caption': caption}
                files = {'photo': (filename, f, 'image/jpeg')}
                send_image_response = requests.post(self.urls['pic'], data=payload, files=files)

            response_json = json.loads(send_image_response.text)

            if response_json['ok']:
                info_dict = {
                    'chat_id': str(response_json['result']['chat']['id']),
                    'message_id': str(response_json['result']['message_id'])
                }
                return 'OK', info_dict
            else:
                response_json.pop('ok')
                return 'ERROR', response_json

    def edit_image_message(self, chat_id: str,
                           message_id: str,
                           base64_encoded_image,
                           filename: str = '') -> Tuple[str, Dict[str, Any]]:
        file_content = base64.b64decode(base64_encoded_image)

        with tempfile.TemporaryFile() as f:
            f.write(file_content)
            f.seek(0)

            payload = {'chat_id': chat_id, 'message_id': message_id,
                       'media': json.dumps({'type': 'photo', 'media': 'attach://media'})}
            files = {'media': (filename, f, 'image/jpeg')}

            edit_image_message_response = requests.post(self.urls['edit_message_media'], data=payload, files=files)
            response_json = json.loads(edit_image_message_response.text)

            if response_json['ok']:
                info_dict = {
                    'chat_id': str(response_json['result']['chat']['id']),
                    'message_id': str(response_json['result']['message_id'])
                }
                return 'OK', info_dict
            else:
                response_json.pop('ok')
                return 'ERROR', response_json

    def pin_message(self, chat_id: str, message_id: str) -> Tuple[str, Dict[str, Any]]:
        payload = {'chat_id': chat_id, 'message_id': message_id, 'disable_notification': True}
        pin_message_response = requests.post(self.urls['pin_message'], data=payload)
        response_json = json.loads(pin_message_response.text)

        if response_json['ok']:
            return 'OK', dict()
        else:
            response_json.pop('ok')
            return 'ERROR', response_json

    def unpin_message(self, chat_id: str, message_id: str) -> Tuple[str, Dict[str, Any]]:
        payload = {'chat_id': chat_id, 'message_id': message_id}
        unpin_message_response = requests.post(self.urls['unpin_message'], data=payload)
        response_json = json.loads(unpin_message_response.text)

        if response_json['ok']:
            info_dict = {
                'chat_id': str(response_json['result']['chat']['id']),
                'message_id': str(response_json['result']['message_id'])
            }
            return 'OK', info_dict
        else:
            response_json.pop('ok')
            return 'ERROR', response_json

    def unpin_all_messages(self, chat_id: str) -> Tuple[str, Dict[str, Any]]:
        payload = {'chat_id': chat_id}
        unpin_message_response = requests.post(self.urls['unpin_all_messages'], data=payload)
        response_json = json.loads(unpin_message_response.text)

        if response_json['ok']:
            return 'OK', dict()
        else:
            response_json.pop('ok')
            return 'ERROR', response_json


if __name__ == '__main__':
    c = ConfigBuilder()
    t = TelegramBot(config=c.build())
    response = t.send_text_message(message='hello world')
    print(response)
    the_chat_id = response[1]['chat_id']
    the_message_id = response[1]['message_id']

    with open("tests/ic5070.jpg", "rb") as image_file, open("tests/m42.jpg", "rb") as second_image_file:
        encoded_string = base64.b64encode(image_file.read())
        response = t.send_image_message(encoded_string, 'ic5070.jpg')
        print(response)

        response = t.pin_message(chat_id=the_chat_id, message_id=the_message_id)
        print(response)

        encoded_string = base64.b64encode(second_image_file.read())
        response = t.edit_image_message(chat_id=the_chat_id, message_id=the_message_id,
                                        base64_encoded_image=encoded_string,
                                        filename='m42.jpg')
        print(response)

        response = t.unpin_message(chat_id=the_chat_id, message_id=the_message_id)
        print(response)
