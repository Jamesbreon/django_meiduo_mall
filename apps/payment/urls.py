from django.conf.urls import url
from . import views


urlpatterns = [
    # 跳转到支付页面
    url(r'^payment/(?P<order_id>\d+)/$', views.AlipayPaymentView.as_view()),
    # 支付成功
    url(r'^payment/status/$', views.PaymentSuccessView.as_view()),
]