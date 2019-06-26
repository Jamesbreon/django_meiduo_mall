from rest_framework import serializers
from fdfs_client.client import Fdfs_client
from django.conf import settings

from goods.models import SKUImage, SKU


class SKUImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = ['id', 'sku', 'image']

    # sku: 2
    # image: (binary)
    def create(self, validated_data):
        image = validated_data.pop('image')
        image_content = image.read()
        conn = Fdfs_client(settings.FDFS_CONFIG_PATH)
        ret = conn.upload_by_buffer(image_content)

        if not ret.get('Status') == 'Upload successed.':
            raise serializers.ValidationError('文件上传失败')

        image_url = ret.get('Remote file_id')
        validated_data['image'] = image_url
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image = validated_data.pop('image')
        image_content = image.read()
        conn = Fdfs_client(settings.FDFS_CONFIG_PATH)
        ret = conn.upload_by_buffer(image_content)
        if not ret.get('Status') == 'Upload successed.':
            raise serializers.ValidationError('文件上传失败')
        image_url = ret.get('Remote file_id')
        instance.image = image_url
        instance.save()
        return instance


class SKUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'name']
