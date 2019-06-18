from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField()

    # 用户校验
    def validate(self, attrs):
        # # 获取前端传来的数据
        # username = attrs.get('username')
        # passoword = attrs.get('password')
        #
        # # 采用django传统验证方法进行验证
        # authenticate(username=username, passoword=passoword)

        user = authenticate(**attrs)
        if not user:
            raise serializers.ValidationError('用户验证失败')

        # 获取token值
        paylaod = jwt_payload_handler(user)
        jwt_token = jwt_encode_handler(paylaod)
        return {
            'user': user,
            'jwt_token': jwt_token
        }