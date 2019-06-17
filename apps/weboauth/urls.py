# 微博登录
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^weibo/login/$', views.SinaLoginView.as_view()),
    url(r'^sina_callback.html$', views.GetUidView.as_view()),
    url(r'^oauth/sina/user/$', views.SinaUserView.as_view()),

]