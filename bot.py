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


    def on_post(self, req, resp):

        body = req.stream.read()

        receive_params = json.loads(body.decode('utf-8'))

        for msg in receive_params['result']:

            utt=msg['content']['text']

            send_content = {
                'to': [msg['content']['from']],
                'toChannel': 1383378250,  # Fixed value
                'eventType': '138311608800106203',  # Fixed value
                'content': {
                    'contentType': 1,
                    'toType': 1,
                    'text': 'こんにちは',
                },
            }
            send_content = json.dumps(send_content)

            res = requests.post(ENDPOINT_URI, data=send_content,
                                headers=self.header, proxies=PROXIES)

            resp.body = json.dumps('OK')


api = falcon.API()
api.add_route('/callback', CallbackResource())
