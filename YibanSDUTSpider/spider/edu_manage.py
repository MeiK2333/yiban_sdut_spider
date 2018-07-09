# coding=utf-8
import json

from bs4 import BeautifulSoup
from requests import session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from .ehall import Ehall


class EduManage(object):
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
        """ 教务管理系统 """
        rst = self.session.get('http://210.44.191.125/jwglxt/jziotlogin')
        if rst.url.startswith('http://210.44.191.125/jwglxt/xtgl/index_initMenu.html'):
            return True
        return False

    @property
    def logined(self):
        """ 检查登录状态 """
        rst = self.session.get(
            'http://210.44.191.125/jwglxt/xtgl/index_initMenu.html')
        if rst.url == 'http://210.44.191.125/jwglxt/xtgl/index_initMenu.html':
            return True
        return False

    def get_schedule(self, year=-1, semester=-1, parse=True):
        """ 获得个人课表 """
        # 若不填写年份与学期，则按照默认的查询（最近要上的课表）
        url = 'http://210.44.191.125/jwglxt/xkcx/xkmdcx_cxXkmdcxIndex.html?doType=query'
        data = {
            'queryModel.showCount': '100',  # 要是有哪位同学一个学期的课程超过一百门...那就节哀吧
            'queryModel.currentPage': '1',
            'time': '0',
        }
        if year != -1:
            if isinstance(year, str):
                year = year[:4]
            data['xnm'] = str(year)
        if semester != -1:
            if semester == 1:
                data['xqm'] = '3'
            elif semester == 2:
                data['xqm'] = '12'

        rst = self.session.post(url, data=data)
        rjson = json.loads(rst.text)
        if not rjson['items']:
            return None
        if parse:  # 若指定信息 parse，则解析数据
            rdata_list = []
            for i in rjson['items']:
                d = {
                    'year': i.get('xnmc', ''),
                    'semester': i.get('xqmc', ''),
                    'course_code': i.get('kch_id', ''),
                    'course_name': i.get('kcmc', ''),
                    'score': i.get('xf', ''),
                    'state': i.get('kkztmc', ''),
                    'class_time': i.get('sksj', ''),
                    'class_location': i.get('jxdd', ''),
                    'course_category': i.get('kclbmc', ''),
                    'course_nature': i.get('kcxzmc', ''),
                    'course_type': i.get('kklxmc', ''),
                    'class': i.get('jxbmc', ''),
                }
                if i.get('jsxx'):  # parse 任课教师
                    _tmp = i.get('jsxx').split('/')
                    if len(_tmp) == 3:
                        _bh, _xm, _zc = _tmp
                    else:
                        _bh, _xm = _tmp
                        _zc = 'None'
                    d['teacher'] = {
                        'id': _bh,
                        'name': _xm,
                        'title': _zc
                    }
                if i.get('sksj', ''):  # parse 上课时间地点
                    _sj = i.get('sksj', '').split(';')
                    _dd = i.get('jxdd', '').split(';')
                    cnt = len(_sj)
                    _sjdd = []
                    for i in range(cnt):
                        _sj_s = _sj[i].split('{')
                        _sjdd.append({
                            'time': _sj_s[0],
                            'location': _dd[i],
                            'week': _sj_s[1][:-1]
                        })
                    d['time_location'] = _sjdd
                rdata_list.append(d)
            rdata = {
                'data': rdata_list,
                'name': rjson['items'][0].get('xm'),
                'sex': rjson['items'][0].get('xbmc'),
                'user_id': rjson['items'][0].get('xh_id'),
                'grade': rjson['items'][0].get('njdm_id'),
                'major': rjson['items'][0].get('zymc'),
                'class': rjson['items'][0].get('bjmc')
            }
            return rdata
        else:  # 否则以原始形式返回
            return rjson

    def get_cur_week(self):
        """ 获取当前周 """
        self.ehall.session.get(
            'http://ehall.sdut.edu.cn/appShow?appId=4787703225473911')
        rst = self.ehall.session.get(
            'http://ehall.sdut.edu.cn/publicapp/sys/mykbxt/myTimeTable/queryThisWeekCourses.do')
        rst = json.loads(rst.text)
        return {
            'cur_week': rst['weekOfTerm'],
            'year': rst['schoolYearTerm'][:-2],
            'semester': rst['schoolYearTerm'][-1:]
        }

    def get_cur_schedule(self, cur=None):
        """ 获取当前周的课表 """
        data = self.get_cur_week()
        if cur is None:
            cur = data['cur_week']
        year = data['year']
        semester = data['semester']
        # 获取当前学期的全部课表
        all_schedule = self.get_schedule(year=year, semester=semester)
        all_schedule['data'] = week_filter_schedule(all_schedule['data'], cur)
        return {
            'year': year,
            'semester': semester,
            'cur': cur,
            'schedule': all_schedule
        }


def week_filter_schedule(schedule, week):
    """ 查找出所有对应周的课 """
    r_schedule = []
    for c in schedule:
        time_location = c.get('time_location')
        if not time_location:
            continue

        c['time_location'] = []
        for tl in time_location:
            if in_week(tl['week'], week):
                c['time_location'].append(tl)
                continue
        if c['time_location']:
            r_schedule.append(c)
    return r_schedule


def in_week(t, week):
    """ 检查某节课的时间是否在指定周内 """
    t = t.split(',')
    for i in t:
        if i.endswith('(双)'):
            if '-' in i:
                s, e = i[:-4].split('-')
                if week >= int(s) and week <= int(e) and week % 2 == 0:
                    return True
            else:
                if week == int(i[:-4]):
                    return True
        elif i.endswith('(单)'):
            if '-' in i:
                s, e = i[:-4].split('-')
                if week >= int(s) and week <= int(e) and week % 2 == 1:
                    return True
            else:
                if week == int(i[:-4]):
                    return True
        else:
            if '-' in i:
                s, e = i[:-1].split('-')
                if week >= int(s) and week <= int(e):
                    return True
            else:
                if week == int(i[:-1]):
                    return True
    return False
