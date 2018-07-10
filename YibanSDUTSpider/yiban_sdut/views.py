from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from spider import SDUT

from .models import User, UserProfile


@login_required
def index(request):
    return render(request, 'index.html')


def login(request):
    if request.method == 'GET':
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
