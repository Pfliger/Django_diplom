# Дипломный проект по курсу «Django: создание функциональных веб-приложений»

## Для запуска проэкта необходимо:
- установить зависимости 
``` 
pip install requirements.txt
```
- Сделайте миграции 
```
python manage.py migrate
```
- Запустить проект 
```
python manage.py runserver
```

Для запуска тестов воспользуйтесь 
```
pytest
```


# Описание API

## Товар:

url: 
```
/api/v1/products/
```

Создавать и изменять товары могут только администраторы. Смотреть могут все пользователи в том числе неавторизованные.

Есть возможность фильтровать товары по цене и содержимому из названия / описания.



## Отзыв к товару
```
url: /api/v1/product-reviews/
```

Оставлять отзыв к товару могут только авторизованные пользователи. 1 пользователь не может оставлять более 1го отзыва на один и тот же товар.

Отзыв можно фильтровать по ID пользователя, дате создания и ID товара.

Пользователь может обновлять и удалять только свой собственный отзыв.



## Заказы
```
url: /api/v1/orders/
```
Создавать заказы могут только авторизованные пользователи. Админы могут получать все заказы, остальное пользователи только свои.

Заказы можно фильтровать по статусу / общей сумме / дате создания / дате обновления и продуктам из позиций.

Менять статус заказа могут только админы.

## Подборки
``` 
url: /api/v1/product-collections/
```
Создавать подборки могут только админы, остальные пользователи могут только их смотреть.