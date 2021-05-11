import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import Product
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_detail(api_client, product_factory):
    """тест на вывод конкретного продукта"""
    products = product_factory(_quantity=5)
    product_ids = [product.id for product in products]
    id_for_view = product_ids[2]
    url = reverse('products-detail', args=(id_for_view,))
    resp = api_client.get(url)
    result = resp.json()
    assert resp.status_code == HTTP_200_OK
    assert result['id'] == id_for_view


@pytest.mark.django_db
def test_product_list(api_client, product_factory):
    """Тест на вывод списка продуктов"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    resp = api_client.get(url)
    results = resp.json()
    expected_ids = {product.id for product in products}
    results_ids = {product['id'] for product in results}
    assert resp.status_code == HTTP_200_OK
    assert expected_ids == results_ids


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_201_CREATED),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_create(api_client, user_kwargs, expected_status):
    """Тест на создание продукта администратором и невозможность создания пользователем"""
    url = reverse('products-list')
    payload = {
        'name': 'test product',
        'description': 'product description',
        'price': '5000.00'
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == expected_status


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_200_OK),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_update(api_client, product_factory, user_kwargs, expected_status):
    """Тест на изменение продукта администратором и невозможность изменения пользователем"""
    products = product_factory(_quantity=5)
    product_ids = [product.id for product in products]
    id_for_update = product_ids[2]
    url = reverse('products-detail', args=(id_for_update,))
    payload = {
        'name': 'product name update',
        'description': 'product description update',
        'price': 5000.00
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.put(url, payload, format='json')
    assert resp.status_code == expected_status
    if resp.status_code == 200:
        updated_product = Product.objects.get(id=id_for_update)
        assert updated_product.name == payload['name']
        assert updated_product.description == payload['description']
        assert updated_product.price == payload['price']


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_204_NO_CONTENT),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_delete(api_client, product_factory, user_kwargs, expected_status):
    """Тест на удаление продукта администратором и невозможность удаления пользователем"""
    products = product_factory(_quantity=5)
    product_ids = [product.id for product in products]
    id_for_delete = product_ids[2]
    url = reverse('products-detail', args=(id_for_delete,))
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.delete(url, format='json')
    assert resp.status_code == expected_status


@pytest.mark.django_db
def test_product_filter_name(api_client, product_factory):
    """Тест фильтра списка продуктов по имени"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    product_names = [product.name for product in products]
    filter_name = product_names[2]
    filter_name_2 = product_names[3]
    resp1 = api_client.get(url, {'name__iexact': filter_name})
    resp2 = api_client.get(url, {'name__icontains': filter_name_2})
    resp1_json = resp1.json()
    resp2_json = resp2.json()
    result_names_1 = {product['name'] for product in resp1_json}
    result_names_2 = {product['name'] for product in resp2_json}
    assert resp1.status_code == HTTP_200_OK
    assert resp2.status_code == HTTP_200_OK
    assert all(str(filter_name) == str(name) for name in result_names_1)
    assert all(str(filter_name_2) == str(name) for name in result_names_2)


@pytest.mark.django_db
def test_product_filter_description(api_client, product_factory):
    """тест фильтра списка продуктов по описанию"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    product_desc = [product.description for product in products]
    filter_desc = product_desc[2]
    resp = api_client.get(url, {'description__icontains': filter_desc})
    resp_json = resp.json()
    result = {product['description'] for product in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert all(str(filter_desc) == str(desc) for desc in result)


@pytest.mark.django_db
def test_product_filter_price(api_client, product_factory):
    """тест фильтра списка продуктов по цене"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    product_prices = [product.price for product in products]
    filter_price = product_prices[2]
    resp = api_client.get(url, {'price': filter_price})
    resp_2 = api_client.get(url, {'price__lte': filter_price})
    resp_3 = api_client.get(url, {'price__gte': filter_price})
    resp_json = resp.json()
    resp_2_json = resp_2.json()
    resp_3_json = resp_3.json()
    price_exact = {price['price'] for price in resp_json}
    price_lte = {price['price'] for price in resp_2_json}
    price_gte = {price['price'] for price in resp_3_json}
    assert resp.status_code == HTTP_200_OK
    assert all(float(price) == float(filter_price) for price in price_exact)
    assert all(float(price) <= float(filter_price) for price in price_lte)
    assert all(float(price) >= float(filter_price) for price in price_gte)
