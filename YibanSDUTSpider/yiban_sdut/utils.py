import json

import requests

from .config import AppID, AppSecret, redirect_uri


def get_access_token(code):
    url = 'https://openapi.yiban.cn/oauth/access_token'
    data = {
        'client_id': AppID,
        'client_secret': AppSecret,
        'code': code,
        'redirect_uri': redirect_uri,
    }
    req = requests.post(url, data)
    access_token = json.loads(req.text)['access_token']
    return access_token


def get_user_id_by_yiban(access_token):
    url = 'https://openapi.yiban.cn/user/verify_me?access_token=' + access_token
    req = requests.get(url)
    data = json.loads(req.text)
    print(data)
    if data['status'] != 'success':
        return None
    return data['info']['yb_schoolid']
