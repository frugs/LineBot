import json
import os
from logging import DEBUG, StreamHandler, getLogger

import requests

import falcon

# logger
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

ENDPOINT_URI = 'https://trialbot-api.line.me/v1/events'
PROXIES = {
    'http': os.environ.get('FIXIE_URL', ''),
    'https': os.environ.get('FIXIE_URL', '')
}
DOCOMO_API_KEY = os.environ.get('DOCOMO_API_KEY', '')


class CallbackResource(object):
    # line
    header = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Line-ChannelID': os.environ['LINE_CHANNEL_ID'],
        'X-Line-ChannelSecret': os.environ['LINE_CHANNEL_SECRET'],
        'X-Line-Trusted-User-With-ACL': os.environ['LINE_CHANNEL_MID'],
    }

    def _get_image(self, content_id):
        line_url = 'https://trialbot-api.line.me/v1/bot/message/' + content_id + '/content/'

        # 画像の取得
        result = requests.get(line_url, headers=self.header, proxies=PROXIES)

        logger.debug('receive image: {}'.format(result.content))

    def on_post(self, req, resp):

        body = req.stream.read()

        receive_params = json.loads(body.decode('utf-8'))
        logger.debug('receive_params: {}'.format(receive_params))

        for msg in receive_params['result']:

            if msg['content']['contentType'] == 1:  # Text
                utt=msg['content']['text']
                if utt == 'はい':
                    text = '購入しました'
                elif utt == 'いいえ':
                    text = '購入しませんでした'
                else:
                    text = 'よくわかりませんでした'
            elif msg['content']['contentType'] == 2:  # Image
                # Confirm whether purchase or not
                text = 'この商品を購入しますか？'
                self._get_image(msg['content']['id'])
            else:
                text = '未対応の処理'

            send_content = {
                'to': [msg['content']['from']],
                'toChannel': 1383378250,  # Fixed value
                'eventType': '138311608800106203',  # Fixed value
                'content': {
                    'contentType': 1,
                    'toType': 1,
                    'text': text,
                },
            }

            send_content = json.dumps(send_content)

            res = requests.post(ENDPOINT_URI, data=send_content,
                                headers=self.header, proxies=PROXIES)

            resp.body = json.dumps('OK')


api = falcon.API()
api.add_route('/callback', CallbackResource())
