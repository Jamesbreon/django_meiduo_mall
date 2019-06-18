from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from admin.views import user_login_view



urlpatterns = [
    # url(r'^authorizations/$', user_login_view.UserLoginView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
]