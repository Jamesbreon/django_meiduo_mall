from rest_framework import serializers

from goods.models import SpecificationOption


class OptionModelSerializer(serializers.ModelSerializer):
    spec = serializers.StringRelatedField()  # 默认为read_only=True
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value', 'spec_id', 'spec']
