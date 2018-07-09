# coding=utf-8
import datetime
import json

from bs4 import BeautifulSoup
from requests import session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from .ehall import Ehall


class Ecard(object):
    def __init__(self, ehall):
        if not isinstance(ehall, Ehall) or not ehall.logined:
            print("ehall 必须为已经登录的 Ehall 实例")
            return
        cookies = ehall.cookies
        self.ehall = ehall
        self.session = session()
        self.ehall_session = session()
        self.ehall_session.cookies = cookiejar_from_dict(json.loads(cookies))
        self.login()

    def login(self):
        """ 通过网上服务大厅登录至校园卡中心 """
        rst = self.ehall_session.get(
            'http://ehall.sdut.edu.cn/publicapp/sys/xkpyktjc/single_sign.do')
        data = json.loads(rst.text)
        rst = self.session.post(data['url'], data=data)
        if rst.url == 'http://211.64.27.136/SelfSearch/Default.aspx':
            return True
        return False

    @property
    def logined(self):
        url = 'http://211.64.27.136/SelfSearch/EcardInfo/UserBaseInfo_Seach.aspx'
        rst = self.session.get(url)
        return '账号不存在' not in rst.text

    def get_balance(self):
        """ 余额查询 """
        url = 'http://211.64.27.136/SelfSearch/EcardInfo/UserBaseInfo_Seach.aspx'
        rst = self.session.get(url)
        soup = BeautifulSoup(rst.text, 'html.parser')
        ipts = soup.find_all('input')
        data = {
            'user_id': ipts[3].get('value'),
            'name': ipts[4].get('value'),
            'balance': ipts[9].get('value')[:-2].strip()
        }
        return data

    def get_consume_info(self):
        """ 消费详情查询 """
        uid = self.ehall.user_id
        url = 'http://211.64.27.136/SelfSearch/EcardInfo/CONSUMEINFO_SEACH.ASPX?outid=' + uid
        rst = self.session.get(url)
        soup = BeautifulSoup(rst.text, 'html.parser')
        ipts = soup.find_all('input')
        data = {
            'ctl00$ContentPlaceHolder1$ConsumeAscx1$ScriptManager1': 'ctl00$ContentPlaceHolder1$ConsumeAscx1$ScriptManager1|ctl00$ContentPlaceHolder1$ConsumeAscx1$btnSeach',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            'ctl00$ContentPlaceHolder1$ConsumeAscx1$btnSeach': ''
        }
        for ipt in ipts:
            if ipt.get('value'):
                data[ipt.get('name')] = ipt.get('value')
        rst = self.session.post(
            'http://211.64.27.136/SelfSearch/EcardInfo/CONSUMEINFO_SEACH.ASPX?outid=' + uid, data=data)
        soup = BeautifulSoup(rst.text, 'html.parser')
        table = soup.find('table').find_all('table')[3]
        trs = table.find_all('tr')
        rdata = []
        for tr in trs[2:]:
            tds = tr.find_all('td')
            time_s = tds[0].string.split('/')
            if len(time_s[1]) < 2:
                time_s[1] = '0' + time_s[1]
            _d, _t = time_s[2].split()
            if len(_d) < 2:
                _d = '0' + _d
            if len(_t) < 8:
                _t = '0' + _t
            time = '{y}-{m}-{d} {t}'.format(y=time_s[0],
                                            m=time_s[1], d=_d, t=_t)

            rdata.append({
                'time': time[:-3],  # 交易时间
                'reason': tds[1].string,  # 科目描述
                'amount': tds[2].string,  # 交易金额
                'balance': tds[4].string,  # 余额
                'position': tds[7].string,  # 工作站
                'termName': tds[8].string  # 交易终端
            })
        return rdata

    def get_cust_state_info(self, start=None, end=None):
        """ 获得指定时间段内的消费汇总 """
        if end is None:
            end = datetime.date.today().strftime("%Y%m%d")
        # 默认查询一周
        if start is None:
            start = (datetime.date.today() -
                     datetime.timedelta(days=7)).strftime("%Y%m%d")
        url = 'http://211.64.27.136/SelfSearch/EcardInfo/CustStateInfo_Seach.aspx?outid={user_id}'.format(
            user_id=self.ehall.user_id)
        rst = self.session.get(url)
        soup = BeautifulSoup(rst.text, 'html.parser')
        ipts = soup.find_all('input')

        # 将要提交的值填充
        data = {
            'ctl00$ContentPlaceHolder1$CustStateInfoAscx1$ScriptManager1': 'ctl00$ContentPlaceHolder1$CustStateInfoAscx1$ScriptManager1|ctl00$ContentPlaceHolder1$CustStateInfoAscx1$btnSeach',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            'ctl00$ContentPlaceHolder1$CustStateInfoAscx1$btnSeach': ''
        }
        for ipt in ipts:
            if ipt.get('value'):
                data[ipt.get('name')] = ipt.get('value')
        data['ctl00$ContentPlaceHolder1$CustStateInfoAscx1$sDateTime'] = start
        data['ctl00$ContentPlaceHolder1$CustStateInfoAscx1$eDateTime'] = end

        rst = self.session.post(url, data=data)
        soup = BeautifulSoup(rst.text, 'html.parser')
        table = soup.find('table').find_all('table')[3]
        trs = table.find_all('tr')
        rdata = []
        for tr in trs[2:]:
            tds = tr.find_all('td')
            rdata.append({
                'id': tds[0].string,
                'reason': tds[1].string,
                'amount': tds[2].string,
                'ext_1': tds[3].string,
                'ext_2': tds[4].string,
                'ext_3': tds[5].string,
            })
        return rdata
