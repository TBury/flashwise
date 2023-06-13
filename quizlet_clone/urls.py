from django.contrib import admin
from django.urls import path, include
from dj_rest_auth.registration import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("api.urls")),
    path("auth/", include("rest_framework.urls")),
    path("api/register", include("dj_rest_auth.registration.urls")),
]
