from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^search/', include('haystack.urls')),
    url(r'^', include('users.urls', namespace='users')),  # 用户子应用
    url(r'^', include('contents.urls', namespace='contents')), # 主页
    url(r'^', include('verifications.urls', namespace='verifications')),  # 验证码
    url(r'^', include('oanuth.urls', namespace='oanuth')), # qq登录模块
    url(r'^', include('weboauth.urls', namespace='weboauth')),  # 微博登录模块

    url(r'^', include('goods.urls', namespace='goods')),  # 商品模块
    url(r'^', include('carts.urls', namespace='carts')),  # 购物车模块
    url(r'^', include('orders.urls', namespace='orders')),  # 结算清单模块
    url(r'^', include('payment.urls', namespace='payment')),  # 支付模块


]
