from django.shortcuts import render
from django import http
from alipay import AliPay
import os
from django.conf import settings

from meiduo_mall.utils.base_view import Base_view
from orders.models import OrderInfo
from meiduo_mall.utils.response_code import RETCODE
from .models import Payment


# Create your views here.
class AlipayPaymentView(Base_view):

    def get(self, request, order_id):
        user = request.user
        # 校验两个条件
        try:
            order = OrderInfo.objects.get(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'], user=user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('非法请求')

        # 支付宝 dev中设置
        # ALIPAY_APPID = '2016091900551154'
        # ALIPAY_DEBUG = True  # 表示是沙箱环境还是真实支付环境
        # ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
        # ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'

        # 创建支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/key/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)) + '/key/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False 修改为开发模式True
        )
        #
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='哈哈商城%s' % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )

        # 响应登录支付宝连接
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '支付成功', 'alipay_url': alipay_url})


class PaymentSuccessView(Base_view):

    def get(self, request):
        # 获取查询字典
        query_dict = request.GET
        # 将查询QueryDict转成字典格式
        data_dict = query_dict.dict()
        # 将字典中的sign找出
        signature = data_dict.pop("sign")

        # 创建alipay对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/key/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)) + '/key/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False 修改为开发模式True
        )
        # 将签名与data进行校验 返回True 或false 如果失败则说明支付失败
        success = alipay.verify(data_dict, signature)
        # 如果返回true说名支付成功，修改订单状态，将交易信息与订单进行绑定
        if success:
            # 交易订单号
            order_id = data_dict.get('out_trade_no')
            # 支付宝交易流水号
            trade_id = data_dict.get('trade_no')

            try:
                Payment.objects.get(order_id=order_id, trade_id=trade_id)
            except Payment.DoesNotExist:
                # 将支付信息保存到payment中
                Payment.objects.create(
                    order_id=order_id,
                    trade_id=trade_id,
                )
            # 修改支付信息
            OrderInfo.objects.filter(order_id=order_id,
                                     status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

            context = {
                'trade_id': trade_id
            }

            return render(request, 'pay_success.html', context)

        else:
            return http.HttpResponseForbidden('非法请求')
