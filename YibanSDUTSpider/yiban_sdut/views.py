from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render

from spider import SDUT

from .config import AppID, redirect_uri
from .models import User, UserProfile
from .utils import get_access_token, get_user_id_by_yiban


@login_required
def index(request):
    return render(request, 'index.html')


def yiban_login(request):
    state = request.GET.get('state')
    if state is None:
        return redirect('https://openapi.yiban.cn/oauth/authorize?client_id={}&redirect_uri={}&state=true'.format(AppID, redirect_uri))
    code = request.GET.get('code')
    access_token = get_access_token(code)
    user_id = get_user_id_by_yiban(access_token)
    # user_id 为 None 代表没有通过身份验证
    if user_id is None:
        return HttpResponse("请先通过易班的身份认证")
    user = User.objects.filter(username=user_id)
    # 如果之前用户已经登记
    if user:
        auth_login(request, user[0])
        return redirect('/')
    # 否则重定向进行用户登记
    return redirect('/login/?redirect=1')


def login(request):
    if request.method == 'GET':
        # 判断是否为易班 APP 访问, 如果是易班访问, 则重定向至易班登录
        if 'yiban_android' in request.META.get('HTTP_USER_AGENT'):
            if request.GET.get('redirect') is None:
                return redirect('/yiban_login/')

        return render(request, 'login.html')
    user_id = request.POST.get('user_id')
    ehall_pass = request.POST.get('ehall_pass')
    ehall = SDUT.get_ehall(user_id, ehall_pass)
    if ehall and ehall.logined:
        user = User.objects.filter(username=user_id)
        # 若之前此用户没有登录过
        if not user:
            # 创建用户
            user = User(username=user_id)
            user.save()
            # 保存用户 ehall 密码
            user_profile = UserProfile(user=user, ehall_pass=ehall_pass)
            user_profile.save()
        else:
            user = user[0]
        # 更新 ehall 密码
        user.user_profile.ehall_pass = ehall_pass
        user.user_profile.save()
        auth_login(request, user)
        return JsonResponse({
            'code': 0,
            'msg': 'success'
        })
    return JsonResponse({
        'code': 1,
        'msg': '学号或密码错误'
    })


def logout(request):
    auth_logout(request)
    return redirect('/')
