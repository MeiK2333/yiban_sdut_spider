# coding=utf-8
import json

from bs4 import BeautifulSoup
from requests import session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar


class Ehall(object):
    def __init__(self, cookies=None):
        self.session = session()
        if cookies:
            self.session.cookies = cookiejar_from_dict(json.loads(cookies))
        self._user_id = None
        self._name = None

    def login(self, username, password):
        self.username = username
        self.password = password

        return self.logined or (self.login_auth_server() and self.login_ehall())

    def login_ehall(self):
        """ 通过 AuthServer 登录至 Ehall """
        rst = self.session.get(
            'http://ehall.sdut.edu.cn/login?service=http://ehall.sdut.edu.cn/new/ehall.html', allow_redirects=False)
        if rst.url == 'http://ehall.sdut.edu.cn/new/ehall.html':
            return True
        return False

    def login_auth_server(self):
        """ 登录至 AuthServer """
        # 如果之前的 cookie 已过期，则需要清理掉，否则会无限重定向
        self.session.cookies = cookiejar_from_dict({})
        login_html = self.session.get(
            'http://authserver.sdut.edu.cn/authserver/login')
        soup = BeautifulSoup(login_html.text, 'html.parser')
        ipts = soup.form.find_all('input')
        data = {
            'username': self.username,
            'password': self.password,
            'rememberMe': False
        }
        for ipt in ipts:
            if ipt.get('value'):
                data[ipt.get('name')] = ipt.get('value')

        rst = self.session.post(
            'http://authserver.sdut.edu.cn/authserver/login', data=data)
        # 若页面跳转至首页，则说明登录成功
        if rst.url == 'http://authserver.sdut.edu.cn/authserver/index.do':
            return True
        # 若页面跳转回登录界面，则说明登录失败(用户名或密码错误)
        elif rst.url == 'http://authserver.sdut.edu.cn/authserver/login':
            return False

    def logout(self):
        """ 退出登录 """
        self.session.get(
            'http://authserver.sdut.edu.cn/authserver/logout?service=/authserver/login')

    @property
    def logined(self):
        """ 检查登录状态 """
        login_html = self.session.get(
            'http://authserver.sdut.edu.cn/authserver/login', allow_redirects=False)
        # 判断当前是否登录(自动跳转至首页)
        if login_html.status_code == 302:
            return True
        if login_html.url == 'http://authserver.sdut.edu.cn/authserver/index.do':
            return True
        return False

    @property
    def cookies(self):
        """ 返回 cookies """
        return json.dumps(dict_from_cookiejar(self.session.cookies))

    @property
    def user_id(self):
        """ 获取 user_id （学号） """
        if self._user_id is None:
            rst = self.session.get(
                'http://ehall.sdut.edu.cn/xsfw/sys/swpubapp/userinfo/getConfigUserInfo.do')
            data = json.loads(rst.text)
            self._user_id = data['data'][0]
        return str(self._user_id)

    @property
    def name(self):
        """ 获取姓名信息 """
        if self._name is None:
            rst = self.session.get(
                'http://ehall.sdut.edu.cn/publicapp/sys/myyktzd/api/getOverviewInfo.do')
            rjson = json.loads(rst.text)
            self._name = rjson['datas']['NAME']
        return str(self._name)

    def get_base_info(self):
        """ 获取学生基本信息 """
        rst = self.session.get(
            'http://ehall.sdut.edu.cn/appShow?appId=4585275700341858')
        rst = self.session.get(
            'http://ehall.sdut.edu.cn/xsfw/sys/jbxxapp/modules/infoStudent/getStuBaseInfo.do?requestParamStr={}')
        rjson = json.loads(rst.text)
        return rjson

    def get_family_info(self):
        """ 家庭信息 """
        rst = self.session.get(
            'http://ehall.sdut.edu.cn/appShow?appId=4585275700341858')
        rst = self.session.get(
            'http://ehall.sdut.edu.cn/xsfw/sys/jbxxapp/modules/infoStudent/getStuFamilyInfo.do?requestParamStr={}')
        rjson = json.loads(rst.text)
        return rjson
