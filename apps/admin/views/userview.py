from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from admin.serializers.user_serializer import UserSerializer
from users.models import User


class MyPage(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'pagesize'
    page_size = 2
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'lists': data,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'pagesize': self.page_size
        })


class UserListView(ListAPIView):  # (GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # 自定义分页器
    pagination_class = MyPage

    # 根据前端传来的keyword对数据集进行过滤
    def get_queryset(self):
        # 获取前端传来的keyword
        keyword = self.request.query_params.get('keyword')
        if keyword:

            return self.queryset.filter(username__contains=keyword)

        return self.queryset.all()


    # def get(self, request):
    #     # 获取查询数据集
    #     user_qs = self.get_queryset()
    #     # 分页
    #     # 获取分页后查询子集
    #     page = self.paginate_queryset(user_qs)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     # 获取序列化数据
    #     serializer = self.get_serializer(user_qs, many=True)
    #     # 返回序列化数据
    #     return Response(serializer.data)
