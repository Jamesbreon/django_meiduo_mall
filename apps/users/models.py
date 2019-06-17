from django.db import models
from django.contrib.auth.models import AbstractUser

from meiduo_mall.utils.models import BaseModels
# Create your models here.


class User(AbstractUser):

    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号码')

    # 如果已完成迁移后，修改models中字段，必须在新增字段中增加default默认值，或设置为None
    email_active = models.BooleanField(default=False, verbose_name='邮箱是否激活')

    # 添加默认地址字段
    default_address = models.ForeignKey('Address', related_name='users',
                                        null=True,
                                        blank=True,
                                        on_delete=models.SET_NULL,
                                        verbose_name='默认地址')

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModels):
    """用户地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='addresses', verbose_name='用户')

    title = models.CharField(max_length=20, verbose_name='地址名称')

    receiver = models.CharField(max_length=20, verbose_name='收货人')

    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT,
                                 related_name='province_addresses', verbose_name='省')

    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT,
                             related_name='city_addresses', verbose_name='市')

    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT,
                                 related_name='district_addresses', verbose_name='区')

    place = models.CharField(max_length=50, verbose_name='地址')

    mobile = models.CharField(max_length=11, verbose_name='手机')

    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        # 将地址更改时间进行降序排序 从最新更改时间向下排序
        ordering = ['-update_date']


