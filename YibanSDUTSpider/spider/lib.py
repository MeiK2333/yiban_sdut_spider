# coding=utf-8
import json

from bs4 import BeautifulSoup
from requests import session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from .ehall import Ehall


class Lib(object):
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
        """ 通过统一登录平台登录至图书馆 """
        rst = self.session.get(
            'http://authserver.sdut.edu.cn/authserver/login?service=http%3A%2F%2F222.206.65.12%2Freader%2Fhwthau.php')
        if rst.url == 'http://222.206.65.12/reader/redr_info.php':
            return True
        return False

    def logout(self):
        self.session.get('http://222.206.65.12/reader/logout.php')

    @property
    def logined(self):
        """ 检查登录状态 """
        rst = self.session.get('http://222.206.65.12/reader/redr_info.php')
        if rst.url == 'http://222.206.65.12/reader/redr_info.php':
            return True
        return False

    def get_borrow_info(self):
        """ 获取当前借书详情 """
        rst = self.session.get(
            'http://222.206.65.12/reader/book_lst.php')
        soup = BeautifulSoup(rst.text, 'html.parser')
        table = soup.find('table')
        rdata = []
        trs = table.find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            if len(tds) < 5:  # 判断是否有书
                break
            rdata.append({
                'title': tds[1].find('a').string,  # 图书名
                'author': tds[1].text[len(tds[1].find('a').string) + 3:],  # 作者
                'borrowDate': tds[2].string.split()[0],  # 借书日期(xxxx-yy-zz)
                'backDate': tds[3].string.split()[0],  # 应还日期(xxxx-yy-zz)
                'borrowCnt': tds[4].string,  # 续借次数
                'site': tds[5].string  # 借书地点
            })
        return rdata

    def get_borrow_history(self):
        """ 获取历史借阅 """
        data = {
            'para_string': 'all',
            'topage': '1'
        }
        rst = self.session.post(
            'http://222.206.65.12/reader/book_hist.php', data=data)
        soup = BeautifulSoup(rst.text, 'html.parser')
        table = soup.find('table')
        rdata = []
        trs = table.find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            if len(tds) < 5:
                break
            rdata.append({
                'barCode': tds[1].string,
                'title': tds[2].string,
                'bookUrl': 'http://222.206.65.12' + tds[2].find('a').get('href')[2:],
                'author': tds[3].string,
                'borrowDate': tds[4].string,
                'backDate': tds[5].string,
                'site': tds[6].string
            })
        return rdata
