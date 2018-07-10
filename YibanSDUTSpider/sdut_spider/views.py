import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from spider import SDUT, Dormitory, Ecard, EduManage, Lib, Logistics

from .utils import api_access, api_error, schedule_parser


@login_required
def card_balance(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    ecard = SDUT.get_object(Ecard, user_id, ehall_pass)
    if ecard and ecard.logined:
        return api_access('校园卡余额', ecard.get_balance()['balance'], '元', '/api/card/info/')
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def card_info(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    ecard = SDUT.get_object(Ecard, user_id, ehall_pass)
    if ecard and ecard.logined:
        return JsonResponse({
            "data": ecard.get_consume_info(),
            "name": "校园卡消费记录",
            "type": "list"
        })
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def energy(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    logistics = SDUT.get_object(Logistics, user_id, ehall_pass)
    if logistics and logistics.logined:
        return api_access('宿舍电量', logistics.get_energy()['energy'], '度', '/api/energy/info/')
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def energy_info(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    logistics = SDUT.get_object(Logistics, user_id, ehall_pass)
    if logistics and logistics.logined:
        return JsonResponse({
            "data": logistics.get_energy(),
            "name": "宿舍电量",
            "type": "dict"
        })
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def borrow(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    lib = SDUT.get_object(Lib, user_id, ehall_pass)
    if lib and lib.logined:
        return JsonResponse({
            'data': lib.get_borrow_info(),
            'name': '图书借阅',
            'type': 'list'
        })
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def borrow_history(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    lib = SDUT.get_object(Lib, user_id, ehall_pass)
    if lib and lib.logined:
        return JsonResponse({
            'data': lib.get_borrow_history(),
            'name': '图书借阅历史',
            'type': 'list'
        })
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def dorm_health(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    dormitory = SDUT.get_object(Dormitory, user_id, ehall_pass)
    if dormitory and dormitory.logined:
        return JsonResponse({
            'data': dormitory.get_dorm_health(),
            'name': '宿舍卫生分数',
            'type': 'list'
        })
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def schedule(request, cur=None):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    edu_manage = SDUT.get_object(EduManage, user_id, ehall_pass)
    if edu_manage and edu_manage.logined:
        data = edu_manage.get_cur_schedule(cur=cur)
        cur = data['cur']
        data['schedule']['data'] = schedule_parser(data['schedule']['data'])
        return JsonResponse({
            'data': data,
            'name': '课程表',
            'type': 'list'
        })
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def cust_state_info(request, delta=7):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    ecard = SDUT.get_object(Ecard, user_id, ehall_pass)
    if ecard and ecard.logined:
        start = (datetime.date.today() -
                 datetime.timedelta(days=delta)).strftime("%Y%m%d")
        return JsonResponse({
            'data': ecard.get_cust_state_info(start=start),
            'name': '交易汇总',
            'type': 'dict'
        })
    return api_error("获取失败, 请检查密码是否正确")
