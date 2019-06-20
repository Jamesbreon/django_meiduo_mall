from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
from datetime import timedelta
import pytz


from users.models import User
from orders.models import OrderInfo
from goods.models import GoodsVisitCount
from admin.serializers.home_serializers import GoodsVisitSerializer


class HomeView(ViewSet):

    # GET
    # /meiduo_admin/statistical/total_count/
    @action(methods=['get'], detail=False)
    def total_count(self, request):
        # 获取用户总数
        tz = pytz.timezone(settings.TIME_ZONE)
        count = User.objects.filter(is_active=True).count()
        # 获取日期(获取UTC时间)
        date = timezone.now().astimezone(tz)
        return Response({
            'count': count,
            'date': date.date(),
        })

    # 日增用户统计
    # statistical/day_increment/
    # GET
    @action(methods=['get'], detail=False)
    def day_increment(self, request):
        # 获取当前时间 获取的是UTC时间
        tz = pytz.timezone(settings.TIME_ZONE)
        cur_date = timezone.now().astimezone(tz)
        date = cur_date.replace(hour=0, minute=0, second=0, tzinfo=tz)

        print(date)
        # 查询出当天时间新增用户
        count = User.objects.filter(date_joined__gte=date).count()

        return Response({
            'count': count,
            'date': date.date()
        })

    # 日活跃统计
    # statistical/day_active/
    # GET
    @action(methods=['get'], detail=False)
    def day_active(self, request):
        # 获取当前时间
        # 获取当前时区对象
        tz = pytz.timezone(settings.TIME_ZONE)
        cur_date = timezone.now().astimezone(tz)
        date = cur_date.replace(hour=0, minute=0, second=0, tzinfo=tz)

        # 查询出当天的用户
        count = User.objects.filter(last_login__gte=date).count()

        return Response({
            'count': count,
            'date': cur_date.date()
        })

    # 下单用户统计
    # statistical/day_orders/
    @action(methods=['get'], detail=False)
    def day_orders(self, request):
        # 统计下单的用户数量
        # 1 多查一
        user_list = []
        order_list = OrderInfo.objects.all()
        for order in order_list:
            user_list.append(order.user)

        # 将用户列表进行去重
        count = len(set(user_list))

        # 2 一查多
        # user_list = User.objects.filter(orderin)
        # count = len(set(user_list))
        # 获取当前时间
        tz = pytz.timezone(settings.TIME_ZONE)
        cur_date = timezone.now().astimezone(tz)

        return Response({
            'count': count,
            'date': cur_date.date()
        })

    # 月增用户统计
    # statistical/month_increment/
    # GET
    @action(methods=['get'], detail=False)
    def month_increment(self, request):
        # 获取当前时间
        tz = pytz.timezone(settings.TIME_ZONE)
        cur_date = timezone.now().astimezone(tz)
        # 将当前时间向前推移30天，包括当天
        start_date = cur_date.replace(hour=0, minute=0, second=0, tzinfo=tz) - timedelta(days=29)
        # 查询出过去30天每天的新增用户
        user_list = []
        for index in range(30):
            date = start_date + timedelta(days=index)
            count = User.objects.filter(date_joined__gte=date, date_joined__lt=date + timedelta(days=1)).count()
            user_list.append({
                'count': count,
                'date': date.date()
            })
        # 数据格式为列表套字典
        return Response(user_list)

    # 日商品分类访问量
    # statistical/goods_day_views/
    # GET
    # @action(methods=['get'], detail=False)
    # def goods_day_views(self, request):
    #     # 1 获取当前时间
    #     tz = pytz.timezone(settings.TIME_ZONE)
    #     cur_date = timezone.now().astimezone(tz)
    #     visit_date = cur_date.replace(hour=0, minute=0, second=0, tzinfo=tz).date()
    #     # 获取当天的商品分类
    #     goodsvisit_qs = GoodsVisitCount.objects.filter(date=visit_date)
    #     category_list = []
    #     for goodvisit in goodsvisit_qs:
    #         category = goodvisit.category
    #         category_list.append({
    #             'category': category.name,
    #             'count': goodvisit.count,
    #         })
    #     return Response(category_list)

    @action(methods=['get'], detail=False)
    def goods_day_views(self, request):
        # 1 获取当前时间
        tz = pytz.timezone(settings.TIME_ZONE)
        cur_date = timezone.now().astimezone(tz)
        visit_date = cur_date.replace(hour=0, minute=0, second=0, tzinfo=tz).date()
        # 获取当天的商品分类
        goodsvisit_qs = GoodsVisitCount.objects.filter(date=visit_date)

        # 创建序列化对象
        serializer = GoodsVisitSerializer(goodsvisit_qs, many=True)

        return Response(serializer.data)
