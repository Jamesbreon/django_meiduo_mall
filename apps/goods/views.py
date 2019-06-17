from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django import http

from contents.utils import get_categories
from .utils import get_breadcrumb
from .models import GoodsCategory, SKU, GoodsVisitCount
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.base_view import Base_view
from orders.models import OrderInfo, OrderGoods


class ListView(View):

    def get(self, request, category_id, page_num):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('获取失败')
        sort = request.GET.get('sort')
        if sort == 'price':
            sort = 'price'
        elif sort == 'hot':
            sort = '-sales'
        else:
            sort = 'create_date'
        # 商品sku
        sku_qs = category.sku_set.filter(is_launched=True).order_by(sort)

        # 分页： 创建分页器
        paginator = Paginator(sku_qs, 5)
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，默认给用户404
            return http.HttpResponseNotFound('empty page')

        # 获取列表页总页数
        total_page = paginator.num_pages

        context = {
            'categories': get_categories(),  # 频道分类
            'breadcrumb': get_breadcrumb(category),  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'list.html', context)


class HotView(View):

    def get(self, request, category_id):
        # category_id 为三级商品分类
        # 根据分类获取sku
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('Goods Category Does Not Exist')

        hot_skus_qs = SKU.objects.filter(category=category, is_launched=True).order_by('-sales')[:2]

        hot_skus = []
        for sku in hot_skus_qs:
            hot_skus.append({
                'id': sku.id,
                'name': sku.name,
                'caption': sku.caption,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


class SKUDetailView(View):

    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        category = sku.category
        spu = sku.spu

        # 通过skuid去查询ordergoods中的评论
        # order_goods = OrderGoods.objects.filter(sku_id=sku_id)
        # for order_good in order_goods:
        #     order = order_good.order
        #     comment = order_good.comment
        #     username = order_good.is_anonymous
        #     if comment:
        #         sku.comment = comment
        #     if username is False:
        #         sku.username = '匿名用户'
        #     else:
        #         sku.username = order.user.username

        # # 根据sku_id查用户,将名字渲染到评论
        # order_qs = OrderInfo.objects.filter(sku_id=sku_id)
        # for order in order_qs:
        #     sku.name = order.user.username


        """1.准备当前商品的规格选项列表 [8, 11]"""
        # 获取出当前正显示的sku商品的规格选项id列表
        current_sku_spec_qs = sku.specs.order_by('spec_id')
        current_sku_option_ids = []  # [8, 11]
        for current_sku_spec in current_sku_spec_qs:
            current_sku_option_ids.append(current_sku_spec.option_id)

        """2.构造规格选择仓库
        {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        """
        # 构造规格选择仓库
        temp_sku_qs = spu.sku_set.all()  # 获取当前spu下的所有sku
        # 选项仓库大字典
        spec_sku_map = {}  # {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        for temp_sku in temp_sku_qs:
            # 查询每一个sku的规格数据
            temp_spec_qs = temp_sku.specs.order_by('spec_id')
            temp_sku_option_ids = []  # 用来包装每个sku的选项值
            for temp_spec in temp_spec_qs:
                temp_sku_option_ids.append(temp_spec.option_id)
            spec_sku_map[tuple(temp_sku_option_ids)] = temp_sku.id

        """3.组合 并找到sku_id 绑定"""
        spu_spec_qs = spu.specs.order_by('id')  # 获取当前spu中的所有规格

        for index, spec in enumerate(spu_spec_qs):  # 遍历当前所有的规格
            spec_option_qs = spec.options.all()  # 获取当前规格中的所有选项
            temp_option_ids = current_sku_option_ids[:]  # 复制一个新的当前显示商品的规格选项列表
            for option in spec_option_qs:  # 遍历当前规格下的所有选项
                temp_option_ids[index] = option.id  # [8, 12]
                option.sku_id = spec_sku_map.get(tuple(temp_option_ids))  # 给每个选项对象绑定下他sku_id属性

            spec.spec_options = spec_option_qs  # 把规格下的所有选项绑定到规格对象的spec_options属性上
        context = {
            'categories': get_categories(),
            'breadcrumb': get_breadcrumb(category),
            'spu': spu,
            'sku': sku,
            'category': category,
            'spec_qs': spu_spec_qs,  # 当前商品的所有规格数据
        }
        return render(request, 'detail.html', context)


class DetailVisitView(View):
    """
    统计分类商品访问量是统计一天内该类别的商品被访问的次数
    """

    def post(self, request, category_id):

        # 校验category_id
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数无效')
        # 处理逻辑
        # 1 将category在表中仅从查找
        today_date = timezone.now()  # 获取当天时间
        try:
            # 如果表中有记录则count +=1
            good_count = GoodsVisitCount.objects.get(date=today_date, category=category)
        except GoodsVisitCount.DoesNotExist:
            # 2 如果不能在表中查到，则直接在表中创建该条记录
            good_count = GoodsVisitCount(category=category)
        good_count.count += 1
        good_count.save()
        # 返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


# 用户中心订单详情
class UserOrderInfoView(Base_view):
    def get(self, request, page_num):

        user = request.user
        # 从数据库中获取订单
        orders_qs = OrderInfo.objects.filter(user=user).order_by('-create_date')

        # 分页： 创建分页器
        paginator = Paginator(orders_qs, 2)

        for order in orders_qs:
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            for order_sku in order_skus:
                # 订单小记
                order_sku.amount = order_sku.count * order_sku.price
                # 动态增加图片
                # order_sku.default_image = order_sku.sku.default_image.url
            # 动态给order增加属性
            order.order_skus = order_skus
            order.status_name = OrderInfo.ORDER_STATUS[order.status]
            order.pay_method_name = OrderInfo.PAY_METHOD[order.pay_method]

        try:
            page_orders = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，默认给用户404
            return http.HttpResponseNotFound('empty page')

        # 总页数
        total_page = paginator.num_pages
        context = {
            'page_orders': page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }

        return render(request, 'user_center_order.html', context)


# 获取商品评价详情
class GetCommnetView(View):

    def get(self, request, sku_id):

        orders_goods = OrderGoods.objects.filter(sku_id=sku_id)
        if not orders_goods:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '此商品暂无评论'})
        comment_list = []
        # 拿到订单
        for orders_good in orders_goods:
            # 一一对应拿到comment和socore
            order = orders_good.order
            comment_list.append({
                'score': orders_good.score,
                'comment': orders_good.comment,
                'username': order.user.username
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'comment_list': comment_list})
