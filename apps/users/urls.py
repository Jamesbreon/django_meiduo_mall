from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 校验用户名是否重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    # 校验电话是否重复
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 登录页面
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    # 登出页面
    url(r'^logout/$', views.LogoutView.as_view()),

    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),

    # email模块
    url(r'^emails/$', views.VerifyEmailView.as_view()),

    # email 激活验证
    url(r'^emails/verification/$', views.Check_Verify_Email.as_view()),

    # 收货地址
    url(r'^addresses/$', views.AdressesView.as_view(), name='address'),

    # 查找地区市
    url(r'^areas/$', views.AreaView.as_view()),

    # 增加收获地址
    url(r'^addresses/create/$', views.CreateAddressView.as_view()),

    # 修改地址
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateAddressView.as_view()),

    # 设置默认你地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.SetDefaultAddressView.as_view()),

    # 设置title
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.SetTitleView.as_view()),

    # 修改密码展示页面
    url(r'^password/$', views.ChangePasswordView.as_view()),

    # 展示最近浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),

    # 找回密码
    url(r'^find_password/$', views.FindePasswordView.as_view()),
    # 找回密码第一步
    url(r'^accounts/(?P<account>[a-zA-Z0-9_-]{5,20})/sms/token/$', views.StepOneView.as_view()),

    # 找回密码验证短信验证码
    url(r'^accounts/(?P<username>1[3-9]\d{9})/password/token/$', views.CheckSMSCode.as_view()),

    # 设置密码
    url(r'^users/(?P<userid>\d+)/password/$', views.SetPassword.as_view())

]