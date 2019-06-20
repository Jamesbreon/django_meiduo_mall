from rest_framework import serializers

from goods.models import GoodsVisitCount


#
class GoodsVisitSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField()
    category = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GoodsVisitCount
        fields = ['category', 'count']
