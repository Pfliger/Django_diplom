from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class OrderStatusChoices(models.TextChoices):
    NEW = "NEW", "Открыто"
    IN_PROGRESS = "IN_PROGRESS", "Выполняется"
    DONE = "DONE", "Выполнен"


class TimestampFields(models.Model):
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)

    class Meta:
        abstract = True


class Product(TimestampFields):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class ProductReview(TimestampFields):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name='Товар')
    review = models.TextField(verbose_name='Текст отзыва')
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Оценка')

    def __str__(self):
        return f'ID_{self.id} - ({self.product} - {self.user})'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ["user", "product"]


class ProductOrderPosition(models.Model):
    product = models.ForeignKey(Product, related_name='orders', on_delete=models.CASCADE, verbose_name='Товар')
    order = models.ForeignKey("Order", related_name='positions', on_delete=models.CASCADE, verbose_name='Заказ')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Позиция'
        verbose_name_plural = 'Позиции'


class Order(TimestampFields):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
    order_status = models.TextField(choices=OrderStatusChoices.choices, default=OrderStatusChoices.NEW,
                                    verbose_name='Статус')
    products = models.ManyToManyField(Product, related_name='order',
                                      through=ProductOrderPosition, verbose_name='Позиции')
    total = models.DecimalField(verbose_name='Общая сумма', null=True, decimal_places=2, max_digits=10)

    def __str__(self):
        return f'ID_{self.id} - {self.user}, total - {self.total}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class ProductCollection(TimestampFields):
    title = models.CharField(verbose_name='Заголовок', max_length=200)
    text = models.TextField(verbose_name='Текст')
    products = models.ManyToManyField('Product', verbose_name='Продукты', related_name='product_collections')

    def __str__(self):
        return f'ID_{self.id} - {self.title}'

    class Meta:
        verbose_name = 'Подборка товаров'
        verbose_name_plural = 'Подборки товаров'
