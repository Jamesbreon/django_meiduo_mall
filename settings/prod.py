import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(sys.path)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
# print(sys.path)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ab=pie8l(kpf-tr0jvy1*-fltp1*9cnz&9fev=f4naly-dygdw'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
# 生产环境
DEBUG = False

ALLOWED_HOSTS = ['www.meiduo.site']


# Application definition
# 追加导包路径

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    'users.apps.UsersConfig',
    'oanuth.apps.OanuthConfig',  # 注册QQ认证子应用
    'weboauth.apps.WeboauthConfig',  # 微博登录子应用
    'areas.apps.AreasConfig',  # 注册省市区查询子应用
    'contents.apps.ContentsConfig',  # 注册首页内容子应用
    'goods.apps.GoodsConfig',  # 注册商品子应用
    'orders.apps.OrdersConfig',  # 订单子应用
    'payment.apps.PaymentConfig',  # 支付宝支付子应用

    'haystack',  # 全文检索
    'django_crontab', # 页面静态化任务定时器

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        # 'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 补充Jinja2模版引擎环境
            'environment': 'meiduo_mall.utils.jinja2_env.jinja2_environment',
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# 配置mysql数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '172.16.253.167',
        'PORT': 3306,
        'USER': 'leroylsy',
        'PASSWORD': '123321lsy',
        'NAME': 'meiduo_test',
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '172.16.253.167',
        'PORT': 8306,
        'USER': 'root',
        'PASSWORD': 'mysql',
        'NAME': 'meiduo_test',
    },
}

# 配置读写分离路由
DATABASE_ROUTERS = ['meiduo_mall.utils.db_router.MasterSlaveDBRouter']


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# USE_TZ = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


# 配置redis数据库
CACHES = {
    # 默认的redis配置项 采用0号数据库
    "default": {
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": 'redis://127.0.0.1/0',
        "OPTIONS": {
            "CLIENT_CLASS": 'django_redis.client.DefaultClient',
        }
    },
    # 保持状态的session的Redis配置项，采用1号数据库
    "session": {
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": "redis://127.0.0.1/1",
        "OPTIONS": {
            "CLIENT_CLASS": 'django_redis.client.DefaultClient',
        }
    },
    "verify_cache": {  # 验证码
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": "redis://127.0.0.1/2",
        "OPTIONS": {
            "CLIENT_CLASS": 'django_redis.client.DefaultClient',
        }
    },
    "history": {   # 用户浏览记录
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": "redis://127.0.0.1/3",
        "OPTIONS": {
            "CLIENT_CLASS": 'django_redis.client.DefaultClient',
        }
    },
    "carts": {   # 购物车
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": "redis://127.0.0.1/4",
        "OPTIONS": {
            "CLIENT_CLASS": 'django_redis.client.DefaultClient',
        }
    },
}

# 修改session存储机制，用redis保存
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 使用名为 session的redis配置项存储session数据
SESSION_CACHE_ALIAS = "session"

# 配置工程日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}


# 自定义User模型在迁移前需要
AUTH_USER_MODEL = 'users.User'

# 配置登录页面的url
LOGIN_URL = '/login/'

# 配置自定义认证后端 多账号登录
AUTHENTICATION_BACKENDS = ['users.utils.MulitUserAuthciate']

# qq登录获取openid注册信息
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'


# 微博登录获取openid注册信息
# App Key：3196849291
# App Secret：71991ff4c65e2f0b5108c1a70358461e
SINA_CLIENT_ID = '3196849291'
SINA_CLIENT_SECRET = '71991ff4c65e2f0b5108c1a70358461e'
SINA_REDIRECT_URI = 'http://www.meiduo.site:8000/sina_callback.html'


# 配置发送邮件
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # 指定邮件后端
EMAIL_HOST = 'smtp.163.com' # 发邮件主机
EMAIL_PORT = 25 # 发邮件端口
EMAIL_HOST_USER = '15626546266@163.com' # 授权的邮箱
EMAIL_HOST_PASSWORD = '123321lsy' # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '美多商城<15626546266@163.com>' # 发件人抬头

# 激活验证码
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'

# 配置自定义文件存储类
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.image_fastdfs.FastDFSStorage'

# fastDFS的真实ip
FDFS_BASE_URL = 'http://172.16.253.167:8888/'


# Haystack elasticsearch 全文检索配置项
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://172.16.253.167:9200/',  # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo_mall',  # Elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# 控制分页
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5


# 支付宝支付配置项
ALIPAY_APPID = '2016092900625230'
ALIPAY_DEBUG = True  # 表示是沙箱环境还是真实支付环境
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'

# 配置静态页面生成定时器
CRONJOBS = [
    # 每1分钟生成一次首页静态文件
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log'))
]
# 配置定时器编码，解决中文错乱问题
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'

# 配置收集静态文件存放目录
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')