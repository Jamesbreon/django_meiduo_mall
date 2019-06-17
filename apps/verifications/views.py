from django.views import View
from django_redis import get_redis_connection
from django import http
from meiduo_mall.utils.response_code import RETCODE
from random import randint
from meiduo_mall.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import send_sms_code
from verifications.constants import REDIS_TIME_EXPIRE


# Create your views here.
class ImageCodeView(View):

    def get(self, request, uuid):
        # 1 接受前端传来的数据
        name, text, image = captcha.generate_captcha()
        # 2 生成随机验证码
        # 3 将随机验证码保存到redis数据库中以备后续校验使用
        redis_conn = get_redis_connection('verify_cache')
        redis_conn.setex('image_%s' % uuid, REDIS_TIME_EXPIRE, text)

        # 4 将image返回到前端进行渲染
        return http.HttpResponse(image, content_type='image/png')


class SMSCodeView(View):

    def get(self, request, mobile):
        # 1获取参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        redis_conn = get_redis_connection('verify_cache')

        # 2校验

        # 防止恶意短时间内连续发送短信验证码，则对电话号码进行检验
        mobile_flag = redis_conn.get('flag_%s' % mobile)

        if mobile_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '访问过于频繁'})

        if all([image_code_client, uuid]) is False:
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        # 校验没问题后将image_code 与redis保存的进行比较

        image_code_server = redis_conn.get('image_%s' % uuid)
        # 为了防止一个验证码可以进行多次验证，在取到后应立即删除
        redis_conn.delete('image_%s' % uuid)

        # 如果image_code_server为None 则表示 验证码过期
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '验证码过期'})

        # 从redis取出的数据为byte类型需要解码
        image_code_server = image_code_server.decode()

        # 验证码不区分大小写，则全部转为小写再进行比较
        if image_code_server.lower() != image_code_client.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码错误'})

        # 3 生成6位随机数
        sms_code = '%06d' % randint(0, 999999)

        # print 为测试用
        print(sms_code)

        # # 3.1 将sms_code 保存到数据库 以备后续校验
        # redis_conn.setex('sms_%s' % mobile, REDIS_TIME_EXPIRE, sms_code)
        #
        # # 3.2 为了防止连续恶意发送验证码，将电话号码做标记存入redis
        # redis_conn.setex('flag_%s' % mobile, 60, 1)

        # 3.3 采用Pipline对访问redis进行优化
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, REDIS_TIME_EXPIRE, sms_code)
        pl.setex('flag_%s' % mobile, 60, 1)
        # 执行管道，否则将不会提交
        pl.execute()

        # 4 由容联云生成验证码
        # 采用容联云通讯发短信验证码

        # 使用容联云 发送短信验证码
        # 以下代码会对容联云服务器发送请求，因此会造成堵塞，前端验证码倒计时响应缓慢，
        # 采用 celery 异步发送 降低响应时间
        # CCP().send_template_sms(mobile, [sms_code, REDIS_TIME_EXPIRE // 60], 1)

        # 调用celery 异步发送短信
        send_sms_code.delay(mobile, sms_code)
        # 5 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '成功'})



