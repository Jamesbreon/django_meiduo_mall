from rest_framework import serializers
from fdfs_client.client import Fdfs_client
from django.conf import settings

from goods.models import Brand


class BrandModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

    def create(self, validated_data):
        """
        name: 1
        first_letter: 1
        logo: (binary)
        :param validated_data: 
        :return: 
        """
        # 获取前端传来的图像对象
        logo = validated_data.pop('logo')
        content = logo.read()
        # 将图片对象上传到fdfs
        conn = Fdfs_client(settings.FDFS_CONFIG_PATH)
        ret = conn.upload_by_buffer(content)
        # 校验图片是否上传成功
        if not ret.get('Status') == 'Upload successed.':
            raise serializers.ValidationError('文件上传失败')
        url = ret.get('Remote file_id')
        validated_data['logo'] = url
        # 如果上传成功则创建新的对象
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # name: xiaomi
        # first_letter: X
        # logo: (binary)

        logo = validated_data.pop('logo')
        logo_content = logo.read()

        # 图片上传
        conn = Fdfs_client(settings.FDFS_CONFIG_PATH)
        ret = conn.upload_by_buffer(logo_content)
        if not ret.get('Status') == 'Upload successed.':
            raise serializers.ValidationError('文件上传失败')

        url = ret.get('Remote file_id')
        instance.logo = url
        instance.save()
        return instance