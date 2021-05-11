from django_filters import rest_framework as filters
from store.models import Product, ProductReview, Order


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'price': ['exact', 'lte', 'gte'],
            'name': ['exact', 'iexact', 'icontains'],
            'description': ['icontains']
        }


class ProductReviewFilter(filters.FilterSet):
    class Meta:
        model = ProductReview
        fields = {
            'user': ['exact'],
            'created_at': ['date'],
            'product': ['exact'],
        }


class OrderFilter(filters.FilterSet):

    class Meta:
        model = Order
        fields = {
            'order_status': ['iexact'],
            'total': ['exact', 'lte', 'gte'],
            'created_at': ['date'],
            'updated_at': ['date'],
            'products__id': ['exact']
        }
