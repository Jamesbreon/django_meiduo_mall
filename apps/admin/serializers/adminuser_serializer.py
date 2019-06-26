from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password

from users.models import User


class AdminUserSerializer(serializers.ModelSerializer):
    """
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set",
        related_query_name="user",
    )

    """

    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'email',
                  'mobile',

                  'password',
                  'groups',
                  'user_permissions',
                  ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # 创建用户需要将密码进行加密一级设置管理权限因此要重新create方法
    def create(self, validated_data):
        # password = validated_data.get('password')
        # validated_data['password'] = make_password(password)
        # validated_data['is_staff'] = True
        # return super().create(validated_data)
        groups = validated_data.pop('groups')
        user_permission = validated_data.pop('user_permissions')
        admin_user = User.objects.create_superuser(**validated_data)

        # 构建中间表数据
        admin_user.groups.set(groups)
        admin_user.user_permissions.set(user_permission)
        return admin_user

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            validated_data['password'] = make_password(password)
        else:
            validated_data['password'] = instance.password
        return super().update(instance, validated_data)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']
