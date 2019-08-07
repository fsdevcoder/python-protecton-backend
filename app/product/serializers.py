from rest_framework import serializers

from core.models import Tag, Product


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product objects"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Product
        fields = ('id', 'title', 'tags', 'price', 'link')
        read_only_fields = ('id',)


class ProductDetailSerializer(ProductSerializer):
    """Serializer for Product details"""
    tags = TagSerializer(many=True, read_only=True)
