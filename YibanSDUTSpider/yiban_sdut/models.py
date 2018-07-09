from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ehall_pass = models.CharField(max_length=128)


class UserCache(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=128)
    value = models.CharField(max_length=10240)
    updated_at = models.DateTimeField(auto_now=True)


def get_user_cache(user):
    user_cache = UserCache.objects.filter(user=user)
    user_cache_dict = {}
    for cache in user_cache:
        user_cache_dict[cache.key] = cache.value
    return user_cache_dict


def set_user_cache(user, key, value):
    user_cache = UserCache.objects.filter(user=user, key=key)
    if user_cache:
        user_cache = user_cache[0]
        user_cache.value = value
    else:
        user_cache = UserCache(user=user, key=key, value=value)
    user_cache.save()
