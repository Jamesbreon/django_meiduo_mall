import json
import base64
import pickle
from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection


from meiduo_mall.utils.response_code import RETCODE
from goods.models import SKU


class CartsView(View):

    def post(self, request):

        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        user = request.user

        # 校验前端传来的数据
        if all([sku_id, count]) is False:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '缺少必要参数'})
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品不存在'})

        if isinstance(count, int) is False:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数格式错误'})

        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数有误')
        # 逻辑处理
        # 1 登录用户存储到redis中
        if user.is_authenticated:
            """
            hash:{sku_id:count}
            set:{sku_id, sku_id}
            """
            # 连接数据库
            conn_redis = get_redis_connection('carts')
            # 将购物车保存到redis中
            # conn_redis.hincrby('user_%s' % user.id, sku_id, count)
            #
            # # 将selected为True的sku_id 保存到set集合
            # if selected:
            #     conn_redis.sadd('selected_%s' % user.id, sku_id)
            pl = conn_redis.pipeline()
            pl.hincrby('user_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})

        else:
            # 2 未登录用户的存储cookie中
            """
            数据格式：
            {
                sku_id:{'sku_count':1,select’:True}
            }
            """
            # 将获取到的sku_id 在存储的cookie中查询，如果存在则sku_count += count
            # cookie中的key和value都是加密后的字符串
            carts_str = request.COOKIES.get('carts')
            # 如果操作过购物车
            if carts_str:
                bytes_carts = carts_str.encode()
                bytes_carts = base64.b64decode(bytes_carts)
                carts_dict = pickle.loads(bytes_carts)
            else:
                # 如果没有操作过购物车
                carts_dict = {}

            if sku_id in carts_dict:
                origin_count = carts_dict[sku_id]['count']
                count += origin_count

            # 如果不存在则将sku_id保存到到cookie中
            carts_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()

            # 响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            response.set_cookie('carts', carts_str)

        return response

    def get(self, request):
        user = request.user
        if user.is_authenticated:

            """
            hash:{sku_id:count}
            set:{sku_id, sku_id}
            """
            # 连接redis数据库
            conn_redis = get_redis_connection('carts')
            # 从hash中取出sku_id 和count   {sku_id:count}
            redis_cart = conn_redis.hgetall('user_%s' % user.id)
            redis_sku = conn_redis.smembers('selected_%s' % user.id)
            # 将格式统一，把从redis格式cookie中的数据格式
            carts_dict = {}
            for sku_id, count in redis_cart.items():
                carts_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_sku,
                }

        else:
            """
            {
                sku_id:{count:1, selected:True}
            }
            """
            # 从cookie中取
            carts_str = request.COOKIES.get('carts')
            # 如果有
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                carts_dict = {}
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '购物车为空'})

        # 从carts_dict中获取所有的key，并在SKU表中查找获取当前的SKU查询集
        sku_qs = SKU.objects.filter(id__in=carts_dict.keys())

        cart_skus = []
        for sku in sku_qs:
            count = carts_dict[sku.id]['count']
            selected = carts_dict[sku.id]['selected']
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),  # 由于前端需要JSON解析所以需要将Decimal转成str
                'count': count,
                'selected': str(selected),
                'amount': str(sku.price * count),
                'default_image_url': sku.default_image.url
            })

        context = {
            'cart_skus': cart_skus
        }

        return render(request, 'cart.html', context)

    def put(self, request):
        """修改购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected')

        # 校验参数
        if all([sku_id, count]) is False:
            return http.JsonResponse({'code': RETCODE.PWDERR, 'errmsg': '缺少必传参数'})

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '商品不存在'})

        if isinstance(count, int) is False:
            return http.JsonResponse({'code': RETCODE.PWDERR, 'errmsg': '参数格式不正确'})

        if isinstance(selected, bool) is False:
            return http.JsonResponse({'code': RETCODE.PWDERR, 'errmsg': '参数格式不正确'})

        # 用户是否登录
        user = request.user
        if user.is_authenticated:

            # 登录用户修改redis中数量
            conn_redis = get_redis_connection('carts')
            pl = conn_redis.pipeline()
            # 修改hash中的count   {sku_id:count}
            # 修改set中的sku_id
            pl.hset('user_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            cart_skus = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,  # 由于前端需要JSON解析所以需要将Decimal转成str
                'count': count,
                'selected': selected,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url
            }

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_skus})
            return response
        else:
            # 未登录修改cookie中count值
            # 1 获取cookie中的值
            carts_str = request.COOKIES.get('carts')
            # 2 将cart_str 转换成 cart_dict
            carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            # 3 修改count值，根据前端传来的count值重新赋值
            if carts_dict:

                carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()
            else:
                carts_dict = {}

            carts_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }
            # 4 返回响应
            # 修改后需要重新渲染
            cart_skus = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,  # 由于前端需要JSON解析所以需要将Decimal转成str
                'count': count,
                'selected': selected,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url
            }

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_skus})
            response.set_cookie('carts', carts_str)
            return response

    def delete(self, request):

        # 获取前端传来的数据
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        user = request.user

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '没有该商品'})
        if user.is_authenticated:
            # 连接redis数据库
            conn_redis = get_redis_connection('carts')
            pl = conn_redis.pipeline()
            # 删除hash中相应的key:value  {sku_id:count}
            pl.hdel('user_%s' % user.id, sku_id)
            # 删除集合中的 sku_id
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除成功'})

        else:
            # 未登录页面 删除传来的sku_id 相应的cookie
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                carts_dict = {}
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除成功'})
            if sku_id in carts_dict:
                del carts_dict[sku_id]
            # 删除sku_id 对应的cookie后 cookie中可能有值有可能没有值
            if carts_dict:
                # 返回响应
                carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()
                response.set_cookie('carts', carts_str)
            # 没有值则删除cookie
            else:
                response.delete_cookie('carts')
            return response


class SelectedAllView(View):

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected')

        if selected:
            if isinstance(selected, bool) is False:
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})

        user = request.user
        if user.is_authenticated:
            # 连接数据库
            conn_redis = get_redis_connection('carts')
            # selected 将hash中sku_id 全都放到set中或将set中全部删除
            # {sku:count}
            cart = conn_redis.hgetall('user_%s' % user.id)
            sku_id_list = cart.keys()
            if selected:
                # 全选
                conn_redis.sadd('selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选
                conn_redis.srem('selected_%s' % user.id, *sku_id_list)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})

        else:
            """
            {
                sku_id:{count:1, selected:True}
            }
            """
            # 用户未登录
            # 将 selected 设置为前端传来的 selected
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
                for sku_id in carts_dict:
                    carts_dict[sku_id]['selected'] = selected
                carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()
                response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
                response.set_cookie('carts', carts_str)

                return response


class SimpleCartsView(View):

    def get(self, request):
        user = request.user
        if user.is_authenticated:

            """
            hash:{sku_id:count}
            set:{sku_id, sku_id}
            """
            # 连接redis数据库
            conn_redis = get_redis_connection('carts')
            # 从hash中取出sku_id 和count   {sku_id:count}
            redis_cart = conn_redis.hgetall('user_%s' % user.id)
            redis_sku = conn_redis.smembers('selected_%s' % user.id)
            # 将格式统一，把从redis格式cookie中的数据格式
            carts_dict = {}
            for sku_id, count in redis_cart.items():
                carts_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_sku,
                }

        else:
            """
            {
                sku_id:{count:1, selected:True}
            }
            """
            # 从cookie中取
            carts_str = request.COOKIES.get('carts')
            # 如果有
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                carts_dict = {}
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '购物车为空'})

        # 从carts_dict中获取所有的key，并在SKU表中查找获取当前的SKU查询集
        sku_qs = SKU.objects.filter(id__in=carts_dict.keys())

        cart_skus = []
        for sku in sku_qs:
            count = carts_dict[sku.id]['count']
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': count,
                'default_image_url': sku.default_image.url
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})
