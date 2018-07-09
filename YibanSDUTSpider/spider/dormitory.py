# coding=utf-8
import json

from bs4 import BeautifulSoup
from requests import session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from .ehall import Ehall


class Dormitory(object):
    def __init__(self, ehall):
        if not isinstance(ehall, Ehall) or not ehall.logined:
            print("ehall 必须为已经登录的 Ehall 实例")
            return
        cookies = ehall.cookies
        self.ehall = ehall
        self.session = session()
        self.session.cookies = cookiejar_from_dict(json.loads(cookies))

        self.get_dorm_info()

    @property
    def logined(self):
        return self.ehall.logined

    def logout(self):
        self.ehall.logout()

    def get_dorm_info(self):
        """ 获取宿舍基本信息 """
        self.session.get(
            'http://ehall.sdut.edu.cn/appShow?appId=4618295887225301')
        data = {
            'requestParams': '{}',
            'actionType': 'MINE',
            'actionName': 'xtsjcx',
            'dataModelAction': 'QUERY',
        }
        # 不知原因的不加这一条就查询不出来
        rst = self.session.post(
            'http://ehall.sdut.edu.cn/xsfw/sys/xszsapp/commoncall/callQuery/xtsjcx-MINE-QUERY.do', data=data)
        data = {
            'requestParams': '{"XSBH":"%s"}' % self.ehall.user_id,
            'actionType': 'MINE',
            'actionName': 'cxxszsdz',
            'dataModelAction': 'QUERY'
        }
        rst = self.session.post(
            'http://ehall.sdut.edu.cn/xsfw/sys/xszsapp/commoncall/callQuery/cxxszsdz-MINE-QUERY.do', data=data)
        rdata = json.loads(rst.text)
        self.campus, self.floor, self.room, self.bed_no = rdata['data'][0]['ZSDZ'].split(
            '/')
        return {
            'campus': self.campus,
            'floor': self.floor,
            'room': self.room,
            'bed_no': self.bed_no
        }

    def get_dorm_health(self):
        """ 获取宿舍卫生分数 """
        self.session.get(
            'http://ehall.sdut.edu.cn/appShow?appId=4606888687682093')
        data = {
            'pageSize': 100,  # 只读取一页，50 条数据
            'pageNumber': 1
        }
        rst = self.session.get(
            'http://ehall.sdut.edu.cn/xsfw/sys/sswsapp/modules/dorm_health_student/sswsxs_sswsxsbg.do', data=data)
        rjson = json.loads(rst.text)
        rlist = []
        for i in rjson['datas']['sswsxs_sswsxsbg']['rows']:
            d = {
                'floor': i['SSLMC'],
                'room': i['FJH'],
                'week': i['ZC'],
                'date': i['JCRQ'],
                'score': i['FS']
            }
            rlist.append(d)
        return rlist
