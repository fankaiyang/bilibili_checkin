import os
import uuid

import requests


def add_buvid(cookie):
    if 'buvid3=' not in cookie:
        cookie += f'; buvid3={uuid.uuid4().hex.upper()}infoc'
    return cookie


def try_share(label, cookie, extra_headers=None, extra_data=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.bilibili.com/',
        'Origin': 'https://www.bilibili.com',
        'Cookie': cookie,
    }
    if extra_headers:
        headers.update(extra_headers)
    data = {
        'bvid': 'BV1VJ8Q6jEgv',
        'csrf': 'abc',
        'eab_x': 2,
        'ramval': 0,
        'source': 'web_normal',
        'ga': 1,
    }
    if extra_data is not None:
        data = extra_data
    try:
        r = requests.post('https://api.bilibili.com/x/web-interface/share/add', headers=headers, data=data, timeout=10)
        body = r.json()
        print(label, 'code=', body.get('code'), 'message=', body.get('message'))
    except Exception as e:
        print(label, 'exception=', repr(e))


cookie = os.environ.get('BILIBILI_COOKIE', '').split('###', 1)[0].strip()
keys = [item.split('=', 1)[0].strip() for item in cookie.split(';') if '=' in item]
print('cookie_key_names=', keys)

csrf = None
for item in cookie.split(';'):
    if item.strip().startswith('bili_jct='):
        csrf = item.strip().split('=', 1)[1]

base_data = {
    'bvid': 'BV1VJ8Q6jEgv',
    'csrf': csrf or '',
    'eab_x': 2,
    'ramval': 0,
    'source': 'web_normal',
    'ga': 1,
}

try_share('original_origin_extra', cookie, extra_data=base_data)
try_share('autobuvid_origin_extra', add_buvid(cookie), extra_data=base_data)
try_share('original_minimal', cookie, extra_data={'bvid': 'BV1VJ8Q6jEgv', 'csrf': csrf or ''})
try_share('autobuvid_minimal', add_buvid(cookie), extra_data={'bvid': 'BV1VJ8Q6jEgv', 'csrf': csrf or ''})
