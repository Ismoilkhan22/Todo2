from django.urls import path

from core.services.auth import *
from core.views import index

urlpatterns = [
    path("", index, name="home"),
    path('login/', sign_in, name='sign-in'),
    path('regis/', sign_up, name='sign-up'),
    path('logout/', sign_out, name='sign-out'),
    path('check/', otp, name='otp'),
    path('resent/', re_otp, name='re-otp')

]