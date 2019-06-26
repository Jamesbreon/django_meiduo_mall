from rest_framework import serializers
from django.contrib.auth.models import Group, Permission


class GroupSerializer(serializers.ModelSerializer):
    """
    原代码中Group模型中，自带manytomanyfield,在创建表数据时会自动创建中间表数据
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
    )
    """
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class PermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']
