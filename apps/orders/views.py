from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django import http

from meiduo_mall.utils.base_view import Base_view
from users.models import Address
from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from .models import OrderGoods, OrderInfo


class OrderSettlementView(Base_view):

    def get(self, request):
        # 收货地址
        # 展示当前用户的收货地址
        user = request.user

        address = Address.objects.filter(user=user, is_deleted=False)
        if address.exists():
            addresses = address
        else:
            addresses = None
        # 商品清单
        # 从redis中查询已勾选的商品和数量
        conn_redis = get_redis_connection('carts')
        # 查询出所以的sku_id  {b'1': b'3'}
        sku_count = conn_redis.hgetall('user_%s' % user.id)
        # 查询勾选的商品id
        sku_ids = conn_redis.smembers('selected_%s' % user.id)
        carts = {}
        for sku_id_bytes in sku_ids:
            carts[int(sku_id_bytes)] = int(sku_count[sku_id_bytes])
        # 在SKU表中查找勾选商品查询集
        skus = SKU.objects.filter(id__in=sku_ids)

        total_count = 0
        total_amount = Decimal('0.00')
        if skus:
            for sku in skus:
                sku.count = carts[sku.id]
                sku.amount = sku.price * sku.count
                # 商品总金额和总数量
                total_count += sku.count
                total_amount += sku.amount

        freight = Decimal('10.00')

        payment_amount = total_amount + freight
        context = {
            'addresses': addresses,
            'skus': skus,
            'count': sku.count,
            'amount': sku.amount,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': payment_amount
        }
        return render(request, 'place_order.html', context)


class OrdersCommitView(Base_view):

    def post(self, request):
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        user = request.user

        if all([address_id, pay_method]) is False:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '缺啥必传参数'})
        try:
            address = Address.objects.get(id=address_id, is_deleted=False)
        except Address.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '收货地址填写有误'})

        # 获取支付方式
        if pay_method not in (OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']):
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '支付方式有误'})

        # 订单状态
        # 如果货到付款则显示UNAPID 如果在线支付则显示待发货
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        total_amount = Decimal('0')
        freight = Decimal('10.00')
        total_count = 0

        # 订单号具有唯一性 下单时间+用户id
        # 用下单时间与用户id进行区分 转换成字符串
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id

        # 手动开始事务
        with transaction.atomic():
            # 创建保存点
            save_point = transaction.savepoint()
            try:
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    total_count=total_count,
                    total_amount=total_amount,
                    address=address,
                    user=user,
                    freight=freight,
                    pay_method=pay_method,
                    status=status
                )

                # 2 修改库存和销量
                # 1 从redis中取出要购买的商品，获取sku_id 和count
                # 从redis中查询已勾选的商品和数量
                conn_redis = get_redis_connection('carts')
                # 查询出所以的sku_id  {b'1': b'3'}
                sku_count = conn_redis.hgetall('user_%s' % user.id)
                # 查询勾选的商品id
                sku_ids = conn_redis.smembers('selected_%s' % user.id)
                carts = {}
                for sku_id_bytes in sku_ids:
                    carts[int(sku_id_bytes)] = int(sku_count[sku_id_bytes])

                for sku_id in carts:
                    while True:
                        # 一次只查询一个sku，用查询集会有缓存问题
                        sku = SKU.objects.get(id=sku_id)
                        # 取出购买数量
                        buy_count = carts[sku_id]
                        # 获取原本的库存
                        origin_stock = sku.stock
                        # 获取原本销量
                        origin_sales = sku.sales
                        # 判断库存是否满足

                        # 创建回滚点
                        if origin_stock < buy_count:
                            # 如果库存不足，回滚，返回响应
                            transaction.savepoint_rollback(save_point)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # 修改库存和销量,定义新库存和新销量
                        new_stock = origin_stock - buy_count
                        new_sales = origin_sales + buy_count
                        # 加入乐观锁
                        # sku.stock = new_stock
                        # sku.sales = new_sales
                        # sku.save()
                        # 乐观锁 ，修改之前用原本数据查询一次
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        # 如果失败,循环给用户机会，直到下单成功
                        if result == 0:
                            continue

                        # 修改spu销量
                        spu = sku.spu
                        spu.sales += buy_count
                        spu.save()

                        # 保存订单中的商品记录
                        OrderGoods.objects.create(
                            count=buy_count,
                            price=sku.price,
                            order=order,
                            sku=sku,
                        )
                        # 累加商品总数量
                        order.total_count += buy_count
                        # 累加商品总价
                        order.total_amount += (sku.price * buy_count)

                        break

                # 累加运费
                order.total_amount += order.freight
                order.save()
            except Exception:
                # 暴力回滚
                transaction.savepoint_rollback(save_point)
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '下单失败'})
            else:
                # 提交事务
                transaction.savepoint_commit(save_point)

        # 订单提交成功后删除redis中数据
        pl = conn_redis.pipeline()
        pl.hdel('user_%s' % user.id, *sku_ids)
        pl.srem('selected_%s' % user.id, *sku_ids)
        # pl.sdelete('selected_%s' % user.id)
        pl.execute()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '提交订单成功', 'order_id': order.order_id})


class OrdersSuccessView(Base_view):

    def get(self, request):
        order_id = request.GET.get('order_id')
        pay_method = request.GET.get('pay_method')
        payment_amount = request.GET.get('payment_amount')

        try:
            order = OrderInfo.objects.get(order_id=order_id, pay_method=pay_method, total_amount=payment_amount)
        except OrderInfo.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '订单查询失败'})

        context = {
            'order_id': order.order_id,
            'payment_amount': order.total_amount,
            'pay_method': order.pay_method
        }
        return render(request, 'order_success.html', context)


# 商品评价
class GoodsCommentView(Base_view):

    def get(self, request):

        order_id = request.GET.get('order_id')
        user = request.user

        # 查到订单
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '订单有误'})

        # 根据order查询商品 sku
        # order_goods = order.skus.all()
        order_goods = order.skus.filter(order=order, is_commented=False)
        skus = []
        for order_good in order_goods:
            sku = order_good.sku
            sku.url = sku.default_image.url
            skus.append({
                'sku_id': sku.id,
                'order_id': order_id,
                'name': sku.name,
                'caption': sku.caption,
                'price': str(sku.price),
                'default_image_url': sku.default_image.url
            })

        return render(request, 'goods_judge.html', {'skus': skus})

    def post(self, request):

        qs_dict = json.loads(request.body.decode())
        order_id = qs_dict.get('order_id')
        sku_id = qs_dict.get('sku_id')
        comment = qs_dict.get('comment')
        score = qs_dict.get('score')
        is_anonymous = qs_dict.get('is_anonymous')
        user = request.user

        # 通过商品的id取到具体商品
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderGoods.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PWDERR, 'errmsg': '评论失败'})
        # 订单中有几个商品就应该有几个评论
        total_count = order.total_count

        # 将具体的评论保存到数据库中
        # comments = []
        try:
            # order_goods = OrderGoods.skus.filter(sku_id=sku_id, is_commented=False)
            order_goods = OrderGoods.objects.get(order=order, sku_id=sku_id)
        except order.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PWDERR, 'errmsg': '评论失败'})
        order_goods.comment = comment
        order_goods.score = score
        order_goods.is_anonymous = is_anonymous
        order_goods.is_commented = True
        order_goods.save()
        # if all(comments) is False:
        #     # 不修改评论
        #     order.status = OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT']
        #     order.save()
        # 根据订单查询到几个商品
        # commented_count = order.skus.filter(is_commented=True).count()
        # if commented_count == total_count:
        order.status = OrderInfo.ORDER_STATUS_ENUM['FINISHED']
        order.save()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
