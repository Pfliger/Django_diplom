import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import ProductCollection
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_collection_detail(api_client, product_collection_factory):
    """Тест на вывод конкретной подборки"""
    product_collection = product_collection_factory(_quantity=5)
    collection_ids = [collection.id for collection in product_collection]
    id_for_view = collection_ids[2]
    url = reverse('product-collections-detail', args=(id_for_view,))
    resp = api_client.get(url)
    result = resp.json()
    assert resp.status_code == HTTP_200_OK
    assert result['id'] == id_for_view


@pytest.mark.django_db
def test_product_collection_list(api_client, product_collection_factory):
    """Тест на вывод списка подборок"""
    product_collections = product_collection_factory(_quantity=5)
    url = reverse('product-collections-list')
    resp = api_client.get(url)
    result = resp.json()
    expected_ids = {collection.id for collection in product_collections}
    result_ids = {collection['id'] for collection in result}
    assert resp.status_code == HTTP_200_OK
    assert expected_ids == result_ids


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_201_CREATED),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_collection_create(api_client, product_factory, user_kwargs, expected_status):
    """Тест на создание подборки администратором и невозможность создания пользователем"""
    url = reverse('product-collections-list')
    products = product_factory(_quantity=5)
    product_ids = [product.id for product in products]
    payload = {
        'title': 'test collection',
        'text': 'collection text',
        'products': [{'product_id': product} for product in product_ids]
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
def test_product_collection_update(api_client, product_collection_factory, product_factory, user_kwargs,
                                   expected_status):
    """Тест на изменение подборки администратором и невозможность изменения пользователем"""
    product_collection = product_collection_factory(_quantity=5)
    collection_ids = [collection.id for collection in product_collection]
    id_for_update = collection_ids[2]
    update_product_list = product_factory(_quantity=3)
    update_product_list_ids = [product.id for product in update_product_list]
    url = reverse('product-collections-detail', args=(id_for_update,))
    payload = {
        'title': 'collection name update',
        'text': 'collection update text',
        'products': [{'product_id': _} for _ in update_product_list_ids]
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.put(url, payload, format='json')
    assert resp.status_code == expected_status
    if resp.status_code == 200:
        updated_collection = ProductCollection.objects.get(id=id_for_update)
        assert updated_collection.title == payload['title']
        assert updated_collection.text == payload['text']
        assert list(updated_collection.products.all()) == update_product_list


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_204_NO_CONTENT),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_collection_delete(api_client, product_collection_factory, user_kwargs, expected_status):
    """Тест на удаление подборки администратором и невозможность удаления пользователем"""
    collections = product_collection_factory(_quantity=5)
    collection_ids = [collection.id for collection in collections]
    collection_id_to_delete = collection_ids[3]
    url = reverse('product-collections-detail', args=(collection_id_to_delete,))
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.delete(url, format='json')
    assert resp.status_code == expected_status
