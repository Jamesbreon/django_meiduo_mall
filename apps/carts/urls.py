from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^carts/$', views.CartsView.as_view()),

    # 购物车全选
    url(r'^carts/selection/$', views.SelectedAllView.as_view()),
    # 简易购物车
    url(r'^carts/simple/$', views.SimpleCartsView.as_view()),

]