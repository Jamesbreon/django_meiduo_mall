import json
import re
from django.contrib.auth.backends import ModelBackend
from .models import User
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData


# 自定义认证子类

# 多用户登录(用户名， 手机)
def username_or_mobile(account):
    if re.match(r'^1[3-9]\d{9}$', account):
        user = User.objects.get(mobile=account)
    else:
        user = User.objects.get(username=account)

    return user


# 创建类继承pModelBackend对输入账户进行验证，若验证通过返回user用户对象
class MulitUserAuthciate(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = username_or_mobile(username)

        # 判断request是否为None
        # 如果为None则访问的是后端，需要判断当前用户是否能具有权限
        if request is None:
            if user.is_staff is False:
                return None

        if user and user.check_password(password):
            return user


# 验证邮箱发送邮件
def gen_verify_url(user):
    serializer = Serializer(settings.SECRET_KEY, 3600)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url


# 激活校验
def verify_activate_email(token):
    serializer = Serializer(settings.SECRET_KEY, 3600)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')

        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user
