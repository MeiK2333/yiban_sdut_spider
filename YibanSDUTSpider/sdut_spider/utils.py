from django.http import JsonResponse


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


def find_first_number(s):
    s = s.split('-')[0]
    return int(s[4:])


def schedule_parser(schedule):
    week_list = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    rdata = []
    # 拆分所有课时
    for i in schedule:
        for j in i['time_location']:
            k = i.copy()
            k['time_location'] = j
            rdata.append(k)
    rdata = sorted(rdata, key=lambda x: (week_list.index(
        x['time_location']['time'][:3]), find_first_number(x['time_location']['time'])))
    return rdata
