from django.conf.urls import url
from . import views


urlpatterns = [
    # 结算清单
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),

    # 提交订单
    url(r'^orders/commit/$', views.OrdersCommitView.as_view()),
    # 提交订单成功
    url(r'^orders/success/$', views.OrdersSuccessView.as_view()),

    # 商品评价
    url(r'^orders/comment/$', views.GoodsCommentView.as_view()),

]