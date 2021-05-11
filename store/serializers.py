from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Order, ProductOrderPosition, ProductCollection, Product, ProductReview


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price')


class ProductReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer(
        read_only=True,
    )

    user = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = ProductReview
        fields = ('id', 'user', 'product', 'review', 'grade', 'created_at', 'updated_at')

    def validate(self, data):
        product_id = self.context['request'].data['product_id']
        if not Product.objects.filter(id=product_id):
            raise serializers.ValidationError('продукта с таким ID не существует')
        return data

    def create(self, validated_data):
        reviews_count = ProductReview.objects.filter(user=self.context['request'].user.id). \
            filter(product=self.context['request'].data['product_id']).count()  #
        if reviews_count >= 1:
            raise ValidationError("Вы оставляли отзыв на этот продукт")
        else:
            validated_data['user'] = self.context['request'].user
            validated_data['product'] = Product.objects.get(id=self.context['request'].data['product_id'])
        return super().create(validated_data)


class ProductCollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = ProductCollection
        fields = ('id', 'title', 'text', 'products', 'created_at', 'updated_at')

    def validate(self, data):
        products_list = self.context['request'].data['products']
        id_list = []
        for product in products_list:
            id_list.append(product.get('product_id'))
            if not Product.objects.filter(id=product['product_id']):
                raise serializers.ValidationError(f"продукта с ID {product['product_id']} не существует")
        if len(set(id_list)) != len(id_list):
            raise serializers.ValidationError("продукты в одной подборке не могут повторяться")

        return data

    def create(self, validated_data):
        product_ids_list = []
        for product in self.context['request'].data['products']:
            product_ids_list.append(product['product_id'])
        validated_data['products'] = Product.objects.filter(id__in=product_ids_list)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        product_ids_list = []
        for product in self.context['request'].data['products']:
            product_ids_list.append(product['product_id'])
        instance.products.clear()
        instance.products.add(*product_ids_list)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductOrderPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrderPosition
        fields = ('id', 'product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    products = ProductOrderPositionSerializer(
        many=True,
        source="positions",
    )

    user = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Order
        fields = ('id', 'user', 'products', 'order_status', 'total', 'created_at', 'updated_at')

    def validate(self, data):
        if not self.context['request'].user.is_staff and 'order_status' in data:
            raise serializers.ValidationError('Статус заказа могут менять только администраторы')
        if 'positions' in data:
            product_ids = set()
            for position in data['positions']:
                product_ids.add(position['product'])
            if len(product_ids) != len(data['positions']):
                raise serializers.ValidationError('Продукты не должны повторяться в заказе')
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        products_data = validated_data.pop('positions')
        validated_data['total'] = 0
        for product in products_data:
            price = Product.objects.get(id=product['product'].id).price
            validated_data['total'] += price * product['quantity']
        order = super().create(validated_data)

        if products_data:
            to_save = []
            for products in products_data:
                to_save.append(ProductOrderPosition(
                    product=products['product'],
                    quantity=products['quantity'],
                    order_id=order.id,
                ))
            ProductOrderPosition.objects.bulk_create(to_save)

            return order

    def update(self, instance, validated_data):
        validated_data['user'] = instance.user
        if 'positions' in validated_data:
            positions_data = validated_data.pop('positions')
            instance.positions.all().delete()
            total = 0
            for product in positions_data:
                price = Product.objects.get(id=product['product'].id).price
                total += price * product['quantity']
            instance.total = total
            if positions_data:
                to_save = []
                for products in positions_data:
                    to_save.append(ProductOrderPosition(
                        product=products['product'],
                        quantity=products['quantity'],
                        order_id=instance.id,
                    ))
                ProductOrderPosition.objects.bulk_create(to_save)

        if 'order_status' in validated_data:
            instance.order_status = validated_data.pop('order_status')
        instance.save()
        return instance
