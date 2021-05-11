from django.contrib import admin
from .models import Order, ProductOrderPosition, ProductCollection, Product, ProductReview


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductReview)
class Product_reviewAdmin(admin.ModelAdmin):
    pass


class ProductOrderPositionInline(admin.TabularInline):
    model = ProductOrderPosition


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductOrderPositionInline]


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    pass
