from rest_framework import serializers

from .models import Category

from .models import Ticket

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

class TicketSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)
    operator_username = serializers.CharField(
        source='operator.username', read_only=True, default=None
    )
    category_name = serializers.CharField(
        source='category.name', read_only=True, default=None
    )

    class Meta:
        model = Ticket
        fields = (
            'id', 'title', 'description',
            'client', 'client_username',
            'operator', 'operator_username',
            'category', 'category_name',
            'status', 'priority',
            'created_at', 'updated_at', 'resolved_at',
        )
        read_only_fields = ('id', 'client', 'created_at', 'updated_at', 'resolved_at')

    def validate_operator(self, value):
        request = self.context['request']
        if value is not None and request.user.role != 'admin':
            raise serializers.ValidationError("Faqat admin operator biriktira oladi.")
        return value

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        # yangi ticket yaratilayotganda tekshiruv shart emas
        if self.instance and user.role == 'client':
            taqiqlangan = {'status', 'operator', 'priority'} & set(attrs.keys())
            if taqiqlangan:
                raise serializers.ValidationError(
                    f"Client quyidagi maydonlarni o'zgartira olmaydi: {', '.join(taqiqlangan)}"
                )
        return attrs