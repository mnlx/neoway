
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('parsedata/', include('parsedata.urls')),
    path('admin/', admin.site.urls),
]