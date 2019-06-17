from django.contrib.auth import login
from django.shortcuts import render, redirect
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django_redis import get_redis_connection

from django.conf import settings
from django.views import View

from users.models import User
from .models import OAuthQQUser
from .utils import get_acess_token, check_openid
import re
from meiduo_mall.utils.response_code import RETCODE
from carts.utils import merge_carts_cookie_2_redis

"""
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'
"""


# QQLoginTool
class QQLoginView(View):

    def get(self, request):
        # next参数的目的是 当登录后会自动跳转到登录前的页面

        next = request.GET.get('next')
        if next is None:
            return http.HttpResponseForbidden('非法访问')

        # 获取qq_url
        qq_code = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                          client_secret=settings.QQ_CLIENT_SECRET,
                          redirect_uri=settings.QQ_REDIRECT_URI,
                          state=next)

        login_url = qq_code.get_qq_url()
        # 前端url var url = this.host + '/qq/authorization/?next=' + next;
        # 将返回的qq_url 以json格式返回给前端
        return http.JsonResponse({'code': RETCODE.OK, 'login_url': login_url})


class GetOpenIdView(View):

    def get(self, request):

        code = request.GET.get('code')

        token_code = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            acess_token = token_code.get_access_token(code)
            openid = token_code.get_open_id(acess_token)
            print(openid)
        except Exception as ret:
            return ret
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # openid 需要加密
            token = get_acess_token(openid)
            # 将加密的唯一表示openid 响应给前端
            return render(request, 'oauth_callback.html', {'openid': token})
        else:
            user = oauth_user.user
            login(request, user)
            next = request.GET.get('state')
            response = redirect(next or '/')
            response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

            # 合并购物车
            merge_carts_cookie_2_redis(request, response)
            return response

    def post(self, request):

        query_dict = request.POST
        mobile = query_dict.get('mobile')
        password = query_dict.get('password')
        sms_code = query_dict.get('sms_code')
        openid = query_dict.get('openid')

        if all([mobile, password, sms_code, openid]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': RETCODE.MOBILEERR, 'errmsg': '请输入正确的手机号码'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'code': RETCODE.PWDERR, 'errmsg': '手机号码或密码不正确'})

        # 检验短信验证码
        # 从数据库中取验证码
        redis_conn = get_redis_connection('verify_cache')
        sms_cod_server = redis_conn.get('sms_%s' % mobile)

        # 为了防止一个短信验证码可以多次验证，取到后应立即删除
        redis_conn.delete('sms_%s' % mobile)

        if sms_cod_server is None:
            return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '验证码过期'})

        # redis取出的为byte类型 进行解码
        sms_cod_server = sms_cod_server.decode()

        if sms_code != sms_cod_server:
            return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码有误'})

        # 校验openid
        openid = check_openid(openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 注册用户
        # 根据mobile查找
        # 1 如果存在则进行绑定
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 2 如果没有则创建用户，再绑定
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        else:
            # 如果用用户则需要检查密码
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        OAuthQQUser.objects.create(user=user, openid=openid)

        login(request, user)
        next = request.GET.get('state')
        response = redirect(next or '/')
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

        # 合并购物车
        merge_carts_cookie_2_redis(request, response)
        return response



