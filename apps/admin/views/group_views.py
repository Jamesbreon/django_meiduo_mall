from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group, Permission
from rest_framework.decorators import action
from rest_framework.response import Response

from admin.serializers.group_serializer import GroupSerializer, PermSerializer
from admin.utils.pagination import MyPage


class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = MyPage

    def get_queryset(self):
        if self.action == 'simple':
            return Permission.objects.order_by('id')
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'simple':
            return PermSerializer
        return self.serializer_class

    @action(methods=['get'], detail=False)
    def simple(self, request):
        queryset = self.get_queryset()
        serializer_class = self.get_serializer_class()
        s = serializer_class(queryset, many=True)
        return Response(s.data)
