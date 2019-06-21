from rest_framework import serializers


from goods.models import SPUSpecification


class SpecSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = ['id', 'name', 'spu', 'spu_id']

        # 反序列化时前端只传来spu_id 与name, 对下面的字段设置为只做序列化输出
        extra_kwargs = {
            'id': {'read_only': True},
            'spu': {'read_only': True}
        }
