from django.urls import path
from . import views

urlpatterns = [
    path("register/",        views.register,         name="register"),
    path("login/",           views.login,            name="login"),
    path("me/",              views.me,               name="me"),
    path("profile/",         views.medical_profile,  name="medical-profile"),

    path("password-reset/request/",views.password_reset_request,name="password-reset-request"),
    path("password-reset/confirm/",views.password_reset_confirm,name="password-reset-confirm"),
    path("profile/image/", views.profile_image, name="profile-image"),
    path("account/settings/", views.account_settings, name="account-settings"),
]
