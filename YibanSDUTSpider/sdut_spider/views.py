from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from spider import SDUT, Ecard, Logistics


def api_access(item, value, unit, url):
    return JsonResponse({
        'code': 0,
        'data': {
            'extra': {
                'type': 'ajax',
                'url': url,
            },
            'item': item,
            'unit': unit,
            'value': value,
        },
        'msg': 'success'
    })


def api_error(msg):
    return JsonResponse({
        "code": 1,
        "msg": msg
    })


@login_required
def card_balance(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    ecard = SDUT.get_object(Ecard, user_id, ehall_pass)
    if ecard and ecard.logined:
        try:
            return api_access('校园卡余额', ecard.get_balance()['balance'], '元', '/api/card/info/')
        except Exception:
            return api_error("无法从上游服务器获得数据, 请检查上游服务器是否正常")
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def card_info(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    ecard = SDUT.get_object(Ecard, user_id, ehall_pass)
    if ecard and ecard.logined:
        try:
            return JsonResponse({
                "data": ecard.get_consume_info(),
                "name": "校园卡消费记录",
                "type": "list"
            })
        except Exception:
            return api_error("无法从上游服务器获得数据, 请检查上游服务器是否正常")
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def energy(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    logistics = SDUT.get_object(Logistics, user_id, ehall_pass)
    if logistics and logistics.logined:
        try:
            return api_access('宿舍电量', logistics.get_energy()['energy'], '度', '/api/energy/info/')
        except Exception:
            return api_error("无法从上游服务器获得数据, 请检查上游服务器是否正常")
    return api_error("获取失败, 请检查密码是否正确")


@login_required
def energy_info(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    logistics = SDUT.get_object(Logistics, user_id, ehall_pass)
    if logistics and logistics.logined:
        try:
            return JsonResponse({
                "data": logistics.get_energy(),
                "name": "宿舍电量",
                "type": "dict"
            })
        except Exception:
            return api_error("无法从上游服务器获得数据, 请检查上游服务器是否正常")
    return api_error("获取失败, 请检查密码是否正确")
