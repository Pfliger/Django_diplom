from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter, ProductReviewFilter, OrderFilter
from .models import Order, ProductCollection, Product, ProductReview
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer, ProductReviewSerializer, ProductCollectionSerializer, \
    OrderSerializer
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsAdminOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            return [IsAdmin()]
        return []


class ProductReviewsViewSet(ModelViewSet):
    queryset = ProductReview.objects.all().select_related('product', 'user')
    serializer_class = ProductReviewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductReviewFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminOrOwner()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return []


class ProductCollectionViewSet(ModelViewSet):
    queryset = ProductCollection.objects.all().prefetch_related('products')
    serializer_class = ProductCollectionSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return []


class OrdersViewSet(ModelViewSet):
    queryset = Order.objects.all().prefetch_related('products').select_related('user')
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            self.queryset = self.queryset.filter(user=request.user)
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['retrieve', 'list', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrOwner()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return []
