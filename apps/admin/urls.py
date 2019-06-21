from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import SimpleRouter


from admin.views.homeview import HomeView
from admin.views.userview import UserListView
from admin.views.sku_views import SKUView, SKUCategoryView, SPUView, GoodsSpecsView
from admin.views.spu_views import SPUViewSet, SPUBrandView, ChannelCategoryView


urlpatterns = [
    # url(r'^authorizations/$', user_login_view.UserLoginView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^users/$', UserListView.as_view()),

    url(r'^skus/$', SKUView.as_view({'get': 'list', 'post': 'create'})),
    url(r'^skus/(?P<pk>\d+)/$', SKUView.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'})),
    url(r'^skus/categories/$', SKUCategoryView.as_view()),
    url(r'^goods/simple/$', SPUView.as_view()),
    url(r'^goods/(?P<pk>\d+)/specs/$', GoodsSpecsView.as_view()),

    url(r'^goods/$', SPUViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^goods/(?P<pk>\d+)/$', SPUViewSet.as_view({'delete': 'destroy', 'get': 'retrieve', 'put': 'update'})),
    url(r'^goods/brands/simple/$', SPUBrandView.as_view()),
    url(r'^goods/channel/categories/$', ChannelCategoryView.as_view()),
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', ChannelCategoryView.as_view()),
]

router = SimpleRouter()
router.register(prefix='statistical', viewset=HomeView, base_name='home')
urlpatterns += router.urls