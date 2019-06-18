from rest_framework.views import APIView
from rest_framework.response import Response

from admin.serializers.user_login_serializers import UserLoginSerializer


class UserLoginView(APIView):

    # 1 序列化对象
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        # 启动校验流程
        serializer.is_valid(raise_exception=True)

        # serializer.data 可获取最终有效数据
        return Response({
            'username': serializer.data.get('user').username,
            'user_id': serializer.data.get('user').id,
            'token': serializer.data.get('jwt_token')
        })
