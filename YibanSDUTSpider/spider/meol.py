# coding=utf-8
import json

from bs4 import BeautifulSoup
from requests import session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from .ehall import Ehall


class Meol(object):
    def __init__(self, ehall):
        if not isinstance(ehall, Ehall) or not ehall.logined:
            print("ehall 必须为已经登录的 Ehall 实例")
            return
        cookies = ehall.cookies
        self.ehall = ehall
        self.session = session()
        self.session.cookies = cookiejar_from_dict(json.loads(cookies))
        self.login()

    def login(self):
        """ 通过统一登录平台登录网络教学平台 """
        rst = self.session.get(
            'http://211.64.28.63/meol/homepage/common/sso_login.jsp')
        if rst.url == 'http://211.64.28.63/meol/homepage/common/../../main.jsp':
            return True
        return False

    @property
    def logined(self):
        """ 检查登录状态 """
        rst = self.session.get('http://211.64.28.63/meol/main.jsp')
        if rst.url == 'http://211.64.28.63/meol/main.jsp':
            return True
        return False

    def get_reminder(self):
        get_url = 'http://211.64.28.63/meol/welcomepage/student/interaction_reminder.jsp'
        rst = self.session.get(get_url)
        soup = BeautifulSoup(rst.text, 'html.parser')
        ul = soup.find(id='reminder')
        spans = ul.find_all('span')
        r1 = int(spans[0].string)
        # r2 = int(spans[1].string)
        lis = ul.find_all('li')
        notice = []
        work = []
        for li in lis[1:1+r1]:
            notice.append({
                'url': 'http://211.64.28.63/meol/main.jsp' + li.a.get('href'),
                'title': li.a.string.strip()
            })
        for li in lis[2+r1:]:
            work.append({
                'url': 'http://211.64.28.63/meol/main.jsp' + li.a.get('href'),
                'title': li.a.string.strip()
            })
        return {
            'notice': notice,
            'work': work
        }
