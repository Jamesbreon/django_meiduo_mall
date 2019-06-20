from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password


from users.models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password']

        # id 字段只做序列化输出
        # password 字段只做序列化输入
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # 设置密码
        password = validated_data.get('password')
        # 对输入的密码进行加密
        password = make_password(password)
        # 设置管理员权限
        validated_data['password'] = password
        validated_data['is_staff'] = True

        instance = self.Meta.model.objects.create_user(**validated_data)
        return instance



