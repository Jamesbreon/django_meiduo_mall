from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission, ContentType
from rest_framework.decorators import action
from rest_framework.response import Response

from admin.serializers.perm_serializer import PermSerializer, ContentTypeSerializer
from admin.utils.pagination import MyPage


class PermViews(ModelViewSet):
    queryset = Permission.objects.order_by('id')
    serializer_class = PermSerializer
    pagination_class = MyPage

    def get_queryset(self):
        if self.action == 'content_types':
            return ContentType.objects.all()
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'content_types':
            return ContentTypeSerializer
        return self.serializer_class

    @action(methods=['get'], detail=False)
    def content_types(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()
        s = serializer(queryset, many=True)
        return Response(s.data)
