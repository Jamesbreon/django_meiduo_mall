from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth import login, logout
from django_redis import get_redis_connection
from django.conf import settings
from django.core.cache import cache
import re
import logging
import json

from users.models import User, Address
from meiduo_mall.utils.response_code import RETCODE
from .utils import MulitUserAuthciate, gen_verify_url, verify_activate_email, username_or_mobile
from celery_tasks.send_emails.tasks import send_verify_mail
from meiduo_mall.utils.base_view import Base_view
from areas.models import Area
from goods.models import SKU
from carts.utils import merge_carts_cookie_2_redis
from orders.models import OrderInfo, OrderGoods

logger = logging.getLogger('django')


class RegisterView(View):

    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):

        query_dict = request.POST
        username = query_dict.get('username')
        password = query_dict.get('password')
        password2 = query_dict.get('password2')
        mobile = query_dict.get('mobile')
        sms_code = query_dict.get('sms_code')
        allow = query_dict.get('allow')
        # 校验传来的参数
        if all([username, password, password2, mobile, sms_code, allow]) is False:
            return HttpResponseForbidden('缺少必须的参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('不正确')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('不正确')

        if password != password2:
            return HttpResponseForbidden('不正确')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('不正确')

        if allow != 'on':
            return HttpResponseForbidden({'code': RETCODE.ALLOWERR, 'errmsg': '用户协议未勾选'})

        # 检验短信验证码
        # 从数据库中取验证码
        redis_conn = get_redis_connection('verify_cache')
        sms_cod_server = redis_conn.get('sms_%s' % mobile)

        # 为了防止一个短信验证码可以多次验证，取到后应立即删除
        redis_conn.delete('sms_%s' % mobile)

        if sms_cod_server is None:
            return HttpResponseForbidden({'code': RETCODE.SMSCODERR, 'errmsg': '验证码过期'})

        # redis取出的为byte类型 进行解码
        sms_cod_server = sms_cod_server.decode()

        if sms_code != sms_cod_server:
            return HttpResponseForbidden({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码有误'})

        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 保持登录状态
        login(request, user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
        return response


# 校验注册是否重名
class UsernameCountView(View):

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        print(count)
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 校验电话是否重复
class MobileCountView(View):

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 用户登录以及多账户登录(usermane or mobile)
class LoginView(View):

    def get(self, request):

        return render(request, 'login.html')

    def post(self, request):

        query_dict = request.POST
        account = query_dict.get('username')
        password = query_dict.get('pwd')
        remembered = query_dict.get('remembered')

        # 采用django自带的用户认证进行用户登录验证
        # authenticate 方法如果验证通过则返回user用户对象，如果没有通过验证则没有返回值，没有返回值默认为None

        authen_obj = MulitUserAuthciate()
        user = authen_obj.authenticate(request, username=account, password=password)
        if user is None:
            # 如果 返回值为None，说明用户或密码错误
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 验证通过保持登录状态
        login(request, user)
        # 如果用户不勾选 记住用户则清除cookie中的sessionid即可，即 设置session的过期时间为0
        if remembered != 'on':
            request.session.set_expiry(0)

        # 登录成功后显示用户名，在返回响应页面时设置带上cookie

        # next参数 用户来源参数，如果有next参数则登录后会进入该页面之前的页面
        next = request.GET.get('next')
        if next:

            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

        # 合并购物车
        merge_carts_cookie_2_redis(request, response)
        return response


# 用户登出
class LogoutView(View):

    def get(self, request):
        # django中自带的登出
        logout(request)

        # 退出登录，重定向到登录也
        response = redirect(reverse('users:login'))

        # 退出登录删除cookie
        response.delete_cookie('username')

        return response


# 用户中心验证第二种方式
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_info.html')


# 需要校验登录索引用LoginRequiredMixin 进行用户登录验证
class VerifyEmailView(LoginRequiredMixin, View):

    # 前端发送的为put请求所以用请求体非表单的方式提起参数
    def put(self, request):
        email = json.loads(request.body.decode())
        to_email = email.get('email')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', to_email):
            return HttpResponseForbidden('email填写有误')
        # print(email)
        # 将email 保存到email字典中
        # user = User.objects()
        # user.email = email
        # user.save()
        # 安全考虑用 乐观锁
        user = request.user
        # 在修改之前，在根据条件查找一次
        User.objects.filter(username=user.username, email='').update(email=to_email)

        verify_url = gen_verify_url(user)

        send_verify_mail.delay(to_email, verify_url)
        data = {
            'code': RETCODE.OK,
            'errmsg': '邮件发送成功'
        }

        return JsonResponse(data)


# 验证信息并改变email_activate的激活状态
class Check_Verify_Email(View):

    def get(self, request):

        token = request.GET.get('token')
        # 校验token值中的email和userid
        if not token:
            return HttpResponseForbidden('缺少token参数')

        user = verify_activate_email(token)
        if not user:
            return HttpResponseForbidden('无效token值')

        # 验证成功后修改邮箱激活状态
        user.email_active = True
        user.save()

        # 返回邮箱验证结果
        return redirect('/info/')


# 收获地址页面
class AdressesView(Base_view):

    # 展示收货地址
    def get(self, request):
        user = request.user
        address_set = Address.objects.filter(user=user, is_deleted=False)

        address_dict_list = []
        for address in address_set:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


# 增加收获地址
class AreaView(Base_view):

    def get(self, request):

        area_id = request.GET.get('area_id')

        # 如果area_id 为None则说明查询的为省
        if area_id is None:

            province_list = cache.get('province_list')
            if not province_list:
                try:
                    province_queryset = Area.objects.filter(parent=None)
                    province_list = []
                    for province_model in province_queryset:
                        province_list.append({'id': province_model.id, 'name': province_model.name})
                        # 响应省份数据
                        # 将省份信息保存到cache中
                    cache.set('province_list', province_list, 3600)

                except Exception as e:
                    logger.error(e)
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})

        else:
            sub_data = cache.get('sub_area' + area_id)
            if sub_data is None:
                try:
                    # 查找所对应的城市
                    city = Area.objects.get(id=area_id)
                    direct_qs = city.subs.all()
                    sub_list = []
                    for direct in direct_qs:
                        sub_list.append({'id': direct.id, 'name': direct.name})

                    sub_data = {
                        'id': city.id,
                        'name': city.name,
                        'subs': sub_list
                    }
                    cache.set('sub_area' + area_id, sub_data, 3600)
                except Area.DoesNotExist:
                    return JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '城市查找错误'})

                    # city.subs.all 等价于 city.city_set.all()  由于是自关联 则必须要重命名 否则会报错
                    # 城市所对应的所有的区

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})


class CreateAddressView(Base_view):

    def post(self, request):

        count = request.user.addresses.count()
        if count >= 20:
            return HttpResponseForbidden('地址数量大于20')

        form_json = json.loads(request.body.decode())
        receiver = form_json.get('receiver')
        province_id = form_json.get('province_id')
        city_id = form_json.get('city_id')
        district_id = form_json.get('district_id')
        place = form_json.get('place')
        mobile = form_json.get('mobile')
        tel = form_json.get('tel')
        email = form_json.get('email')

        # 校验前端传来的数据
        if all([receiver, province_id, city_id, district_id, place, mobile]) is False:
            return JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '缺少必传参数'})

        # 校验电话、 固定电话、 email正确格式
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return HttpResponseForbidden('手机号码格式不正确')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('固定电话格式不正确')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('邮箱格式输入不正确')
        # 逻辑处理
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 查询默认地址，如果没有就将现有的做为默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        address_json = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 返回响应
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'address': address_json})


class UpdateAddressView(Base_view):

    def put(self, request, address_id):

        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('参数email有误')

        try:
            Address.objects.filter(id=address_id).update(
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据

        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    # 删除地址
    def delete(self, request, address_id):
        # 逻辑删除，将is_delete 参数改为True
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

            # 响应删除地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class SetDefaultAddressView(Base_view):

    def put(self, request, address_id):

        try:
            address = Address.objects.get(id=address_id)

            request.user.default_address = address
            request.user.save()

        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '设置默认值失败'})

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置成功'})


# 设置标题
class SetTitleView(Base_view):

    def put(self, request, address_id):

        # 1 接受前端传来的参数
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()

        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '修改失败'})
        # 响应给前端
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '修改成功'})


class ChangePasswordView(Base_view):

    def get(self, request):

        return render(request, 'user_center_pass.html')

    def post(self, request):

        # 接受前端传来的数据
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')

        # 校验数据
        if all([old_password, new_password, new_password2]) is False:
            return JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '缺少必传参数'})

        # 校验密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', old_password):
            return HttpResponseForbidden('密码格式不正确')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return HttpResponseForbidden('密码格式不正确')

        # 查询旧密码是否正确
        user = request.user
        if user.check_password(old_password) is False:
            return JsonResponse({'code': RETCODE.PWDERR, 'errmsg': '密码不正确'})

        if new_password != new_password2:
            return JsonResponse({'code': RETCODE.PWDERR, 'errmsg': '两次密码输入不一致'})

        user.set_password(new_password)
        user.save()

        # 返回响应
        # 1 退出登录，重定向登录页
        logout(request)
        response = redirect(reverse('users:login'))
        # 2 删除cookie信息
        response.delete_cookie('username')
        return response


class UserBrowseHistory(Base_view):
    """保存用户浏览记录"""

    def post(self, request):

        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 校验前端传来的数据
        if sku_id is None:
            return HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('参数有误')

        # 将sku_id 保存到redis中
        # 以列表的方式存储到redis中: key:[sku_id, sku_id, sku_id]
        # 1 连接数据库, 配置 记录用户浏览历史的redis
        conn_redis = get_redis_connection('history')
        # 1.1 创建唯一的key
        key = 'user_%s' % request.user.id
        # 2 储存之前去重 lrem(key, count, value)
        # conn_redis.lrem(key, 0, sku_id)
        # 3 lpush将最新的放到列表最前端
        # conn_redis.lpush(key, sku_id)
        # 4 截取，展示浏览记录时最多展示5个
        # conn_redis.ltrim(key, 0, 4)

        # 多次访问数据库 运用管道技术进行优化
        pl = conn_redis.pipeline()
        pl.lrem(key, 0, sku_id)
        pl.lpush(key, sku_id)
        pl.ltrim(key, 0, 4)
        pl.execute()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

    def get(self, request):

        # 1 从redis中获取保存的sku_id
        user = request.user
        conn_redis = get_redis_connection('history')
        key = 'user_%s' % user.id
        skus_qs = conn_redis.lrange(key, 0, -1)

        skus = []
        # 遍历获取sku_id
        for sku_id in skus_qs:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })

        return JsonResponse({'code': RETCODE.OK, 'errmsg': "OK", 'skus': skus})


# 找回密码
class FindePasswordView(View):

    def get(self, request):
        return render(request, 'find_password.html')


# 找回密码第一步
class StepOneView(View):
    def get(self, request, account):
        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('image_code')
        user = username_or_mobile(account)
        if not user:
            return JsonResponse({'code': RETCODE.USERERR, 'errmsg': '用户名或电话不存在'})

        # 获取电话
        mobile = user.mobile

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK',
                             'mobile': mobile,
                             'access_token': uuid,
                             'image_code': image_code})


class CheckSMSCode(View):
    def get(self, request, username):
        sms_code = request.GET.get('sms_code')
        access_token = request.GET.get('access_token')

        # 校验redis数据库中的手机验证码
        redis_conn = get_redis_connection('verify_cache')
        sms_cod_server = redis_conn.get('sms_%s' % username)

        # 为了防止一个短信验证码可以多次验证，取到后应立即删除
        redis_conn.delete('sms_%s' % username)

        if sms_cod_server is None:
            return HttpResponseForbidden({'code': RETCODE.SMSCODERR, 'errmsg': '验证码过期'})

        # redis取出的为byte类型 进行解码
        sms_cod_server = sms_cod_server.decode()

        if sms_code != sms_cod_server:
            return HttpResponseForbidden({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码有误'})

        user = User.objects.get(mobile=username)

        return JsonResponse({'code': RETCODE.OK,
                             'errmsg': 'OK', 'user_id': user.id,
                             'access_token': access_token})


# 忘记密码第三步  设置密码
class SetPassword(View):

    def post(self, request, userid):
        qs_dict = json.loads(request.body.decode())
        password = qs_dict.get('password')
        password2 = qs_dict.get('password2')
        access_token = qs_dict.get('access_token')

        if all([password, password2, access_token]) is False:
            return JsonResponse({'message': '缺啥参数'})

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'message': '密码格式不正确'})

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password2):
            return JsonResponse({'message': '密码格式正确'})

        if password != password2:
            return HttpResponseForbidden({'message': '密码不一致'})

        # 修改数据库中用户密码
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            return HttpResponseForbidden({'message': '用户不存在'})

        user.set_password(password)
        user.save()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})





