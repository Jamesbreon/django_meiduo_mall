from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User
from admin.serializers.adminuser_serializer import AdminUserSerializer, GroupSerializer
from admin.utils.pagination import MyPage


class AdminUserView(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminUserSerializer
    pagination_class = MyPage

    def get_queryset(self):
        if self.action == 'simple':
            return Group.objects.all()
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'simple':
            return GroupSerializer
        return self.serializer_class

    @action(methods=['get'], detail=False)
    def simple(self,request):
        querset = self.get_queryset()
        serializer_class = self.get_serializer_class()
        s = serializer_class(querset, many=True)
        return Response(s.data)
