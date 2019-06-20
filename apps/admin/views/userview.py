from rest_framework.generics import ListAPIView

from admin.utils.pagination import PagNum
from admin.serializers.user_serializer import UserSerializer


class UserListView(ListAPIView):

    # 自定义分页器
    pagination_class = [PagNum]

    pass