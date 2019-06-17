from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings


def get_acess_token(openid):

    serializer = Serializer(settings.SECRET_KEY, 300)

    token = serializer.dumps(openid)

    acess_token = token.decode()

    return acess_token


def check_openid(token):

    serializer = Serializer(settings.SECRET_KEY, 300)
    try:
        openid = serializer.loads(token)
    except BadData:
        return None
    return openid

