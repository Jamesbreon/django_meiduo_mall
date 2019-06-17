from django.contrib.auth import login
from django.shortcuts import render, redirect
from django import http
from django_redis import get_redis_connection
from django.conf import settings
from django.views import View
import json

from users.models import User
from .models import OAuthSinaUser
from .utils import get_acess_token, check_openid
import re
from meiduo_mall.utils.response_code import RETCODE
from carts.utils import merge_carts_cookie_2_redis
from meiduo_mall.utils.sinaweibopy3 import APIClient


# SinaLoginTool
class SinaLoginView(View):

    def get(self, request):
        # next参数的目的是 当登录后会自动跳转到登录前的页面

        next = request.GET.get('next')
        if next is None:
            return http.HttpResponseForbidden('非法访问')

        # 获取新浪_url
        web_code = APIClient(app_key=settings.SINA_CLIENT_ID,
                             app_secret=settings.SINA_CLIENT_SECRET,
                             redirect_uri=settings.SINA_REDIRECT_URI,
                             )

        login_url = web_code.get_authorize_url()
        # 前端url var url = this.host + '/qq/authorization/?next=' + next;
        # 将返回的qq_url 以json格式返回给前端
        return http.JsonResponse({'code': RETCODE.OK, 'login_url': login_url})


class GetUidView(View):

    def get(self, request):

        code = request.GET.get('code')

        token_code = APIClient(
            app_key=settings.SINA_CLIENT_ID,
            app_secret=settings.SINA_CLIENT_SECRET,
            redirect_uri=settings.SINA_REDIRECT_URI)
        try:
            # 获取acess_token
            result = token_code.request_access_token(code)
            access_token = result.access_token
            # 给access_token需要加密
            token = get_acess_token(access_token)
        except Exception as ret:
            return ret
        try:
            oauth_user = OAuthSinaUser.objects.get(uid=access_token)
        except OAuthSinaUser.DoesNotExist:

            # 将token保存session中以备校验
            key_token = 'token_%s' % code
            request.session[key_token] = token
            return render(request, 'sina_callback.html')
        else:
            user = oauth_user.user
            login(request, user)
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK',
                                          'user_id': user.id,
                                          'username': user.username,
                                          'token': token, })
            response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
            # 合并购物车
            merge_carts_cookie_2_redis(request, response)
            return response


class SinaUserView(View):

    def get(self, request):

        code = request.GET.get('code')
        user = request.user
        key_token = 'token_%s' % code
        token = request.session.get(key_token)

        access_token = check_openid(token)
        if not token:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})
        # 获取之后删除
        # del request.session[key_token]

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK',
                                  'user_id': user.id,
                                  'username': user.username,
                                  'token': token,
                                  'access_token': access_token,
                                  })

    def post(self, request):

        query_dict = json.loads(request.body.decode())
        mobile = query_dict.get('mobile')
        password = query_dict.get('password')
        sms_code = query_dict.get('sms_code')
        access_token = query_dict.get('access_token')

        # 通过acess_token 加密获取token
        token = get_acess_token(access_token)

        if all([mobile, password, sms_code, access_token]) is False:
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

        # 校验acess_token
        # access_token = check_openid(token)
        if not access_token:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的acess_token'})

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

        # 从获取uid
        OAuthSinaUser.objects.create(user=user, uid=access_token)

        login(request, user)
        # next = request.GET.get('state')
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK',
                                      'user_id': user.id,
                                      'username': user.username,
                                      'token': token, })
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

        # 合并购物车
        merge_carts_cookie_2_redis(request, response)

        return response
