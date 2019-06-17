from django.conf.urls import url
from . import views


urlpatterns = [
    # 商品列表url
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view()),
    # 热销排行
    url(r'^hot/(?P<category_id>\d+)/$', views.HotView.as_view()),

    # 统计访问量
    url(r'^detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),

    # 商品详情页面
    url(r'^detail/(?P<sku_id>\d+)/$', views.SKUDetailView.as_view()),

    # 获取商品评价详情
    url(r'^comments/(?P<sku_id>\d+)/$', views.GetCommnetView.as_view()),

    # 用户全部订单展示
    url(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrderInfoView.as_view()),

]