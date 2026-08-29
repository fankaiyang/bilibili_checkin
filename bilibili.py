import uuid

import requests
from loguru import logger

class BilibiliTask:
    def __init__(self, cookie):
        self.cookie = cookie
        self._ensure_buvid()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.bilibili.com/',
            'Cookie': self.cookie
        }
        self.csrf = self._get_csrf()

    def _ensure_buvid(self):
        """Bilibili risk control rejects some endpoints without buvid3."""
        if 'buvid3=' not in self.cookie:
            buvid = uuid.uuid4().hex.upper() + 'infoc'
            self.cookie += f'; buvid3={buvid}'

    def _get_csrf(self):
        for item in self.cookie.split(';'):
            if item.strip().startswith('bili_jct'):
                return item.split('=')[1]
        return None

    def get_user_info(self):
        url = 'https://api.bilibili.com/x/web-interface/nav'
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            res.raise_for_status()
            data = res.json()
            if data['code'] == 0:
                return data['data']
            logger.warning(f"获取用户信息失败: {data.get('message')}")
            return None
        except Exception as e:
            logger.error(f"请求用户信息API异常: {e}")
            return None


    
    def get_dynamic_videos(self):
        # The legacy dynamic/region endpoint now returns -404 from Bilibili.
        # The ranking endpoint is still public and gives fresh videos.
        return self.get_ranking_videos()

    def get_ranking_videos(self):
        url = 'https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all'
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            res.raise_for_status()
            data = res.json()
            if data['code'] == 0:
                return [video['bvid'] for video in data.get('data', {}).get('list', [])]
            return []
        except Exception as e:
            logger.error(f"请求排行榜视频API异常: {e}")
            return []

    def check_video_coin_status(self, bvid):
        url = f'https://api.bilibili.com/x/web-interface/archive/coins?bvid={bvid}'
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            res.raise_for_status()
            data = res.json()
            if data['code'] == 0:
                return data['data']['multiply'] > 0
            return False
        except Exception:
            return False

    def add_coin(self, bvid, num=1, select_like=1):
        if not self.csrf: return False, "Bili_jct(csrf) 未找到"
        url = 'https://api.bilibili.com/x/web-interface/coin/add'
        data = {'bvid': bvid, 'multiply': num, 'select_like': select_like, 'csrf': self.csrf}
        try:
            res = requests.post(url, headers=self.headers, data=data, timeout=10)
            data = res.json()
            if data['code'] == 0:
                return True, "投币成功"
            return False, data.get('message', '投币失败')
        except Exception as e:
            return False, str(e)
            
    def share_video(self, bvid):
        if not self.csrf: return False, "Bili_jct(csrf) 未找到"
        url = 'https://api.bilibili.com/x/web-interface/share/add'
        data = {'bvid': bvid, 'csrf': self.csrf}
        try:
            res = requests.post(url, headers=self.headers, data=data, timeout=10)
            data = res.json()
            if data['code'] == 0:
                return True, "分享成功"
            return False, data.get('message', '分享失败')
        except Exception as e:
            return False, str(e)

    def watch_video(self, bvid):
        url = 'https://api.bilibili.com/x/click-interface/web/heartbeat'
        data = {'bvid': bvid, 'played_time': 30, 'csrf': self.csrf}
        try:
            res = requests.post(url, headers=self.headers, data=data, timeout=10)
            data = res.json()
            if data['code'] == 0:
                return True, "观看成功"
            return False, data.get('message', '观看失败')
        except Exception as e:
            return False, str(e)
            
    def live_sign(self):
        url = 'https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign'
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            data = res.json()
            if data['code'] == 0:
                return True, data.get('data', {}).get('text', '直播签到成功')
            return False, data.get('message', '直播签到失败')
        except Exception as e:
            return False, str(e)

    def manga_sign(self):
        url = 'https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn'
        try:
            res = requests.post(url, headers=self.headers, data={'platform': 'ios'}, timeout=10)
            data = res.json()
            if data['code'] == 0:
                return True, "漫画签到成功"
            return False, data.get('message', '漫画签到失败')
        except Exception as e:
            return False, str(e)
