import requests
import json
import pprint
import os


X_Cybozu_API_Token1 = os.environ.get('X_Cybozu_API_Token1')
X_Cybozu_API_Token2 = os.environ.get('X_Cybozu_API_Token2')
X_Cybozu_Authorization = os.environ.get('X_Cybozu_Authorization')


# get coupons
def get_coupons():
    headers = {'X-Cybozu-API-Token': os.environ.get('X_Cybozu_API_Token1')}
    res = requests.get('https://m-quest.cybozu.com/k/v1/records.json?app=2', headers=headers)
    res_json = json.loads(res.content.decode("utf-8"))
    pprint.pprint(res_json)


def get_coupon_by_id(coupon_id=2):
    headers = {'X-Cybozu-API-Token': os.environ.get('X_Cybozu_API_Token1')}
    res = requests.get('https://m-quest.cybozu.com/k/v1/record.json?app=2&id={}'.format(coupon_id), headers=headers)
    res_json = json.loads(res.content.decode("utf-8"))

    return res_json


def get_user_by_id(user_id=1):
    headers = {'X-Cybozu-API-Token': os.environ.get('X_Cybozu_API_Token2')}
    res = requests.get('https://m-quest.cybozu.com/k/v1/record.json?app=1&id={}'.format(user_id), headers=headers)
    res_json = json.loads(res.content.decode("utf-8"))

    return res_json


def update_user_info(mgold, exp, user_id=1):
    # update mgold, exp
    headers = {'X-Cybozu-Authorization': os.environ.get('X_Cybozu_Authorization'),
               'Content-Type': 'application/json'}
    data = json.dumps({"app": 1, "id": user_id, "record": {'mgold': {'value': mgold}, 'exp': {'value': exp}}})
    res = requests.put('https://m-quest.cybozu.com/k/v1/record.json', data=data, headers=headers)
    res_json = json.loads(res.content.decode("utf-8"))
    pprint.pprint(res_json)


if __name__ == '__main__':
    user = get_user_by_id()
    pprint.pprint(user)
    print(user['record']['mgold'])
    print(user['record']['exp'])
    print()

    coupon = get_coupon_by_id()
    pprint.pprint(coupon)
    print(coupon['record']['name'])

    update_user_info(1000, 1000)