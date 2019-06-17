from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^qq/authorization/$', views.QQLoginView.as_view()),
    url(r'^oauth_callback$', views.GetOpenIdView.as_view()),

]