import json
import os
from logging import DEBUG, StreamHandler, getLogger

import requests
import base64
import falcon
from kintone import *

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

    def _get_image(self, content_id):
        line_url = 'https://trialbot-api.line.me/v1/bot/message/' + content_id + '/content/'

        # 画像の取得
        result = requests.get(line_url, headers=self.header, proxies=PROXIES)

        #logger.debug('receive image: {}'.format(result.content))
        img = result.content

        img = base64.encodestring(img).decode('utf-8')
        content = {'img': img}
        res = requests.post('http://52.196.88.89:8000/scanner', data=json.dumps(content))
        return res.content

    def create_text(self, msg, text):
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
        return send_content

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
                if utt == '買っといてー':
                    logger.debug("Item ID: {}".format(self.item_id))
                    logger.debug("Shop ID: {}".format(self.shop_id))

                    # text=クーポンあるけど使う？
                    coupon = get_coupon_by_id()
                    logger.debug(("Coupon: {}".format(coupon)))
                    coupon_name = coupon['record']['name']['value']
                    text = '{0}があるけど使う？'.format(coupon_name)
                elif utt == 'いいえ':
                    text = '買わなかったよ〜'
                elif utt == '使わない':
                    text = '使わなかったよ'
                elif utt == 'お願い':
                    text = 'クーポン使ったよ'
                    # ger user info
                    user = get_user_by_id()
                    base_mgold, base_exp = int(user['record']['mgold']['value']), int(user['record']['exp']['value'])
                    # update user info
                    mgold = base_mgold - int(int(self.price) * 0.1)
                    exp = base_exp - int(int(self.price) * 0.1)
                    logger.debug('exp: {}, mgold: {}, {},{}'.format(exp, mgold, type(exp), type(mgold)))
                    update_user_info(str(mgold), str(exp))
                else:
                    text = 'よくわかりませんでした'
                send_content = self.create_text(msg, text)
            elif msg['content']['contentType'] == 2:  # Image
                # Confirm whether purchase or not
                decode_data = self._get_image(msg['content']['id'])
                items = decode_data.decode("utf-8").split(',')
                text = 'この{0}円の{1}買う？'.format(items[5],items[4])
                self.shop_id, self.item_id, self.price = items[0], items[1], items[5]
                logger.debug("decode_data: {}".format(decode_data))
                send_content = self.create_text(msg, text)
            else:
                text = '未対応の処理'
                send_content = self.create_sticker(msg, text)

            send_content = json.dumps(send_content)

            res = requests.post(ENDPOINT_URI, data=send_content, headers=self.header, proxies=PROXIES)

            resp.body = json.dumps('OK')


api = falcon.API()
api.add_route('/callback', CallbackResource())
