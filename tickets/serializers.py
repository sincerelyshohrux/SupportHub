from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_name(self, value):
        # bir xil nomli kategoriya ikki marta yaratilmasin
        qs = Category.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Bu nomdagi kategoriya allaqachon mavjud.")
        return value




    