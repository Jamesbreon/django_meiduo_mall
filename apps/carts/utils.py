import base64, pickle
from django_redis import get_redis_connection


# 定义函数：是否需要传参数
def merge_carts_cookie_2_redis(request, response):
    """将cookie中的数据保存到redis中"""
    # 取出cookie中的数据
    carts_str = request.COOKIES.get('carts')
    user = request.user
    # 如果cookie中有数据则进行合并，如果没有则提前响应
    if carts_str:
        carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
    else:
        return
    # 连接redis数据库
    conn_redis = get_redis_connection('carts')
    pl = conn_redis.pipeline()
    # 将cookie中的数据保存到redis中
    # 将cookie中的数据取出
    for sku_id in carts_dict:
        # 将sku_id保存到hash中
        pl.hset('user_%s' % user.id, sku_id, carts_dict[sku_id]['count'])
        if carts_dict[sku_id]['selected']:
            pl.sadd('selected_%s' % user.id, sku_id)
        else:
            pl.srem('selected_%s' % user.id, sku_id)
    # 删除cookie
    pl.execute()
    response.delete_cookie('carts')