from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import SimpleRouter

from admin.views.homeview import HomeView
from admin.views.userview import UserListView
from admin.views.sku_views import SKUView, SKUCategoryView, SPUView, GoodsSpecsView
from admin.views.spu_views import SPUViewSet, SPUBrandView, ChannelCategoryView
from admin.views.specs_views import SpecModelViewSet
from admin.views.option_views import OptionModelViewSet, OptionSimpleView
from admin.views.channel_views import GoodsChannelModelViewSet  # GoodsCategoryOneModelView, ChannelGroupModelView,
from admin.views.brand_views import BrandModelView
from admin.views.orders_views import OrderInfoModelView  # OrderDetailModelView
from admin.views.image_view import ImageView
from admin.views.perm_views import PermViews
from admin.views.group_views import GroupView
from admin.views.adminuser_views import AdminUserView

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

    url(r'^goods/specs/$', SpecModelViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^goods/specs/(?P<pk>\d+)/$',
        SpecModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 规格选项表展示
    url(r'^specs/options/$', OptionModelViewSet.as_view({'get': 'list', 'post': 'create'})),
    # 修改选项规格，获取单一模型
    url(r'^specs/options/(?P<pk>\d+)/$',
        OptionModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 保存规格是需要查询出当前所以规格
    url(r'^goods/specs/simple/$', OptionSimpleView.as_view()),

    # 获取频道信息, 创建新频道
    url(r'^goods/channels/$', GoodsChannelModelViewSet.as_view({'get': 'list', 'post': 'create'})),

    url(r'^goods/channels/(?P<pk>\d+)/$',
        GoodsChannelModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 获取频道信息
    # url(r'^goods/channel_types/$', ChannelGroupModelView.as_view()),
    url(r'^goods/channel_types/$', GoodsChannelModelViewSet.as_view({'get': 'channel_type'})),
    # 获取一级分类
    # url(r'^goods/categories/$', GoodsCategoryOneModelView.as_view()),
    url(r'^goods/categories/$', GoodsChannelModelViewSet.as_view({'get': 'categories'})),

    # 品牌管理： 展示
    url(r'^goods/brands/$', BrandModelView.as_view({'get': 'list', 'post': 'create'})),

    # 获取单一的品牌
    url(r'^goods/brands/(?P<pk>\d+)/$', BrandModelView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 订单管理：获取订单信息
    url(r'^orders/$', OrderInfoModelView.as_view({'get': 'list'})),
    # 获取订单详情
    url(r'^orders/(?P<pk>\d+)/$', OrderInfoModelView.as_view({'get': 'retrieve'})),
    # 修改订单状态
    url(r'^orders/(?P<pk>\d+)/status/$', OrderInfoModelView.as_view({'put': 'partial_update'})),

    # 图片管理
    url(r'^skus/images/$', ImageView.as_view({'get': 'list', 'post': 'create'})),
    # 修改 删除
    url(r'^skus/images/(?P<pk>\d+)/$', ImageView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 新增图片获取当前图片所属sku
    url(r'^skus/simple/$', ImageView.as_view({'get': 'simple'})),

    # 获取权限数据， 新增权限数据
    url(r'^permission/perms/$', PermViews.as_view({'get': 'list', 'post': 'create'})),
    # 修改权限数据
    url(r'^permission/perms/(?P<pk>\d+)/$', PermViews.as_view({'put': 'update', 'delete': 'destroy'})),
    # 获取权限类型
    url(r'^permission/content_types/$', PermViews.as_view({'get': 'content_types'})),

    # 获取分组数据
    url(r'^permission/groups/$', GroupView.as_view({'get': 'list', 'post': 'create'})),
    # 获取当前分组权限及其他数据
    url(r'^permission/groups/(?P<pk>\d+)/$', GroupView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    # 获取权限数据
    url(r'^permission/simple/$', GroupView.as_view({'get': 'simple'})),

    # 获取管理员数据信息
    url(r'^permission/admins/$', AdminUserView.as_view({'get': 'list', 'post': 'create'})),
    # 获取当前admin用户信息
    url(r'^permission/admins/(?P<pk>\d+)/$', AdminUserView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 获取分组信息
    url(r'^permission/groups/simple/$', AdminUserView.as_view({'get': 'simple'})),




]

router = SimpleRouter()
router.register(prefix='statistical', viewset=HomeView, base_name='home')
# router.register(r'^goods/specs/', viewset=SpecModelViewSet, base_name='specs')
# router.register(r'specs/options/', viewset=OptionModelViewSet, base_name='options')
urlpatterns += router.urls
