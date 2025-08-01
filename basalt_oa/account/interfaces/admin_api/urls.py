from django.contrib.auth.views import LogoutView
from django.urls import re_path

from account.interfaces.admin_api.views import (
    RegisterView, LoginView, InitSuperAdminView, MyUserInfoView,
    UserListView, MeInfoView
)

urlpatterns = [
    re_path(r'^register/$', RegisterView.as_view(), name='register'),
    re_path(r'^login/$', LoginView.as_view(), name='login'),
    re_path(r'^myinfo/$', MyUserInfoView.as_view(), name='myinfo'),
    re_path(r'^list/$', UserListView.as_view(), name='user-list'),
    re_path(r'^me/$', MeInfoView.as_view(), name='a_system_me_api'),

]
