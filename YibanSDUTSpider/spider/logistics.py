# coding=utf-8
import datetime
import json

from bs4 import BeautifulSoup
from requests import session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar
from datetime import datetime

from .ehall import Ehall
from .dormitory import Dormitory


class Logistics(object):
    def __init__(self, ehall):
        if not isinstance(ehall, Ehall) or not ehall.logined:
            print("ehall 必须为已经登录的 Ehall 实例")
            return
        self.ehall = ehall
        self.session = session()
        self.login()

    def login(self):
        """ 登录至后勤服务大厅 """
        rst = self.session.get('http://hqfw.sdut.edu.cn/login.aspx')
        soup = BeautifulSoup(rst.text, 'html.parser')
        ipts = soup.find_all('input')
        data = {}
        for ipt in ipts:
            if ipt.get('value'):
                data[ipt.get('name')] = ipt.get('value')
        data['ctl00$MainContent$txtName'] = self.ehall.name
        data['ctl00$MainContent$txtID'] = self.ehall.user_id
        data.pop('ctl00$MainContent$btnCancel')
        rst = self.session.post(
            'http://hqfw.sdut.edu.cn/login.aspx', data=data)
        return '欢迎您,{name}同学'.format(name=self.ehall.name) in rst.text

    @property
    def logined(self):
        rst = self.session.get('http://hqfw.sdut.edu.cn/default.aspx')
        return '欢迎您,{name}同学'.format(name=self.ehall.name) in rst.text

    def get_energy(self, campus=None, floor=None, room=None):
        """ 获取宿舍电量 """
        if not (campus and floor and room):
            dormitory = Dormitory(self.ehall)
            campus = self.get_dormitory_list(
            )[c_dormitory_campus(dormitory.campus)]['campus']
            floor = self.get_dormitory_list()[c_dormitory_campus(
                dormitory.campus)]['floor'][c_dormitory_floor(dormitory.floor)]
            room = c_dormitory_room(dormitory.room)

        if campus not in ['0', '1'] or (floor not in self.get_dormitory_list()['西校区']['floor'].values() and floor not in self.get_dormitory_list()['西校区']['floor'].values()) or not room.isdigit():
            return None

        rst = self.session.get('http://hqfw.sdut.edu.cn/stu_elc.aspx')
        soup = BeautifulSoup(rst.text, 'html.parser')
        ipts = soup.find_all('input')
        data = {}
        for ipt in ipts:
            if ipt.get('value'):
                data[ipt.get('name')] = ipt.get('value')
        data['ctl00$MainContent$campus'] = campus
        data['ctl00$MainContent$buildingwest'] = floor
        data['ctl00$MainContent$roomnumber'] = room
        rst = self.session.post(
            'http://hqfw.sdut.edu.cn/stu_elc.aspx', data=data)
        soup = BeautifulSoup(rst.text, 'html.parser')
        text_area = soup.find(id='MainContent_TextBox1')
        if not text_area:
            return None
        text_area = text_area.string
        values = text_area.split('\n')

        rdata = {}
        for value in values:
            value = value.strip()
            if value.startswith('您所查询的房间为：'):
                rdata['room'] = value[9:-1]
            elif value.startswith('根据您的用电规律'):
                _s = value[16:-2].split(' - ')
                rdata['lower'] = _s[0]
                rdata['upper'] = _s[1]
            elif value.startswith('当前用电状态为：'):
                rdata['status'] = value[8:-1]
            elif value.startswith('在'):
                _a, _b = value.split('，')
                _d = _a[1:-1]
                _e = _b[6:-2]
                rdata['date'] = datetime.strptime(
                    _d, '%Y/%m/%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                rdata['energy'] = _e
        return rdata

    def get_dormitory_list(self):
        """ 返回查询对应列表 """
        return {
            '西校区': {
                'campus': '1',
                'floor': {
                    "1#公寓南楼": "01#南",
                    "1#公寓北楼": "01#北",
                    "2#公寓南楼": "02#南",
                    "2#公寓北楼": "02#北",
                    "3#公寓南楼": "03#南",
                    "3#公寓北楼": "03#北",
                    "4#公寓南楼": "04#南",
                    "4#公寓北楼": "04#北",
                    "5#公寓楼": "05#",
                    "6#公寓楼": "06#",
                    "7#公寓楼": "07#",
                    "8#公寓楼": "08#",
                    "9#公寓楼": "09#",
                    "10#公寓楼": "10#",
                    "11#公寓楼": "11#",
                    "12#公寓楼": "12#",
                    "13#公寓南楼": "13#南",
                    "13#公寓北楼": "13#北",
                    "14#公寓楼": "14#",
                    "15#公寓楼": "15#",
                    "16#公寓楼": "16#",
                    "17#公寓楼": "17#",
                    "18#公寓楼": "18#",
                    "19#公寓楼": "19#",
                    "20#公寓楼": "20#",
                    "21#公寓楼": "21#",
                    "22#公寓楼": "22#",
                    "研究生公寓北楼": "研男#",
                    "研究生公寓南楼": "研女#",
                    "新研究生A座": "A-",
                    "新研究生C座": "C-",
                    "瑞贤园单身楼": "rxy-",
                }
            },
            '东校区': {
                'campus': '0',
                'floor': {
                    '东校区1#公寓楼': 'E01#',
                    '东校区2-3#公寓楼': 'E02#',
                    '东校区4#公寓楼': 'E04#',
                    '东校区6#公寓楼': 'E06#',
                    '东校区8#公寓楼': 'E08#',
                    '东校区9#公寓楼': 'E09#',
                    '东校区10#公寓楼': 'E10#'
                }
            }
        }


def c_dormitory_campus(d_campus):
    return d_campus


def c_dormitory_floor(d_floor):
    floor_dict_0 = {
        '东区1号公寓': '东校区1#公寓楼',
        '东区2号公寓': '东校区2-3#公寓楼',
        '东区4号公寓': '东校区4#公寓楼',
        '东区6号公寓': '东校区6#公寓楼',
        '东区8号公寓': '东校区8#公寓楼',
        '东区9号公寓': '东校区9#公寓楼',
        '东区10号公寓': '东校区10#公寓楼',
    }
    floor_dict_1 = {
        '1号公寓北楼': '1#公寓北楼',
        '1号公寓南楼': '1#公寓南楼',
        '2号公寓北楼': '2#公寓北楼',
        '2号公寓南楼': '2#公寓南楼',
        '3号公寓北楼': '3#公寓北楼',
        '3号公寓南楼': '3#公寓南楼',
        '4号公寓北楼': '4#公寓北楼',
        '4号公寓南楼': '4#公寓南楼',
        '5号公寓': '5#公寓楼',
        '6号公寓': '6#公寓楼',
        '7号公寓': '7#公寓楼',
        '8号公寓': '8#公寓楼',
        '9号公寓': '9#公寓楼',
        '10号公寓': '10#公寓楼',
        '11号公寓': '11#公寓楼',
        '12号公寓': '12#公寓楼',
        '13号公寓北楼': '13#公寓北楼',
        '13号公寓南楼': '13#公寓南楼',
        '14号公寓': '14#公寓楼',
        '15号公寓': '15#公寓楼',
        '16号公寓': '16#公寓楼',
        '17号公寓': '17#公寓楼',
        '18号公寓': '18#公寓楼',
        '19号公寓': '19#公寓楼',
        '20号公寓': '20#公寓楼',
        '21号公寓': '21#公寓楼',
        '22号公寓': '22#公寓楼',
        '研究生北楼': '研究生公寓北楼',
        '研究生南楼': '研究生公寓南楼',
        '研究生A楼': '新研究生A座',
        '研究生C楼': '新研究生C座',
    }
    return floor_dict_0.get(d_floor) or floor_dict_1.get(d_floor)


def c_dormitory_room(d_room):
    return d_room[-4:-1]
