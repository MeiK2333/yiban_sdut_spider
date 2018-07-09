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


def api_error():
    return JsonResponse({
        "code": 1,
        "msg": "获取失败, 请检查密码是否正确"
    })


@login_required
def card_balance(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    ecard = SDUT.get_object(Ecard, user_id, ehall_pass)
    if ecard and ecard.logined:
        return api_access('校园卡余额', ecard.get_balance()['balance'], '元', '/api/card/info/')
    return api_error()


@login_required
def card_info(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    ecard = SDUT.get_object(Ecard, user_id, ehall_pass)
    if ecard and ecard.logined:
        return JsonResponse(
            {
                "data": ecard.get_consume_info(),
                "name": "校园卡消费记录",
                "type": "list"
            }

        )
    return api_error()


@login_required
def energy(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    logistics = SDUT.get_object(Logistics, user_id, ehall_pass)
    if logistics and logistics.logined:
        return api_access('宿舍电量', logistics.get_energy()['energy'], '度', '/api/energy/info/')
    return api_error()


@login_required
def energy_info(request):
    user_id = request.user.username
    ehall_pass = request.user.user_profile.ehall_pass
    logistics = SDUT.get_object(Logistics, user_id, ehall_pass)
    if logistics and logistics.logined:
        return JsonResponse(
            {
                "data": logistics.get_energy(),
                "name": "宿舍电量",
                "type": "dict"
            }

        )
    return api_error()
