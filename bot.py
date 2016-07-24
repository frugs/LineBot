import json
import os
from logging import DEBUG, StreamHandler, getLogger

import requests
import base64
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


class CallbackResource(object):
    # line
    header = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Line-ChannelID': os.environ['LINE_CHANNEL_ID'],
        'X-Line-ChannelSecret': os.environ['LINE_CHANNEL_SECRET'],
        'X-Line-Trusted-User-With-ACL': os.environ['LINE_CHANNEL_MID'],
    }
    item_id, shop_id, price = None, None, 10000
    #state = {"Buy?": False, "Use?": False, "Item": []}
    buy, use, item = False, False, ()

    def create_sticker(self, msg, text):
        send_content = {
                'to': [msg['content']['from']],
                'toChannel': 1383378250,  # Fixed value
                'eventType': '138311608800106203',  # Fixed value
                'content': {
                    'contentType': 8,
                    'contentMetadata': {'SKIP_BADGE_COUNT': 'true', 'STKTXT': '[ビシッ]', 'STKVER': '100', 'AT_RECV_MODE': '2', 'STKID': '13', 'STKPKGID': '1'},
                    'toType': 1,
                    'text': text,
                },
            }
        return send_content

    def on_post(self, req, resp):

        body = req.stream.read()

        receive_params = json.loads(body.decode('utf-8'))
        logger.debug('receive_params: {}'.format(receive_params))

        for msg in receive_params['result']:
            if msg['content']['contentType'] == 1:  # Text
                utt = msg['content']['text']
                text = '未対応の処理'
                send_content = self.create_sticker(msg, text)

            send_content = json.dumps(send_content)

            res = requests.post(ENDPOINT_URI, data=send_content, headers=self.header, proxies=PROXIES)

            resp.body = json.dumps('OK')
            

api = falcon.API()
api.add_route('/callback', CallbackResource())
