from django.conf.urls import url
from admin.views import user_login_view


urlpatterns = [
    url(r'^authorizations/$', user_login_view.UserLoginView.as_view()),
]