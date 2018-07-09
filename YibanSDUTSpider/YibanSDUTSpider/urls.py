from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('yiban_sdut.urls')),
    path('api/', include('sdut_spider.urls')),
    path('admin/', admin.site.urls),
]
