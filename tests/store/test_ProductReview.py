import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_403_FORBIDDEN, \
    HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_review_detail(api_client, product_review_factory):
    """Тест на вывод конкретного отзыва"""
    product_collection = product_review_factory(_quantity=5)
    collection_ids = [collection.id for collection in product_collection]
    id_for_view = collection_ids[2]
    url = reverse('product-reviews-detail', args=(id_for_view,))
    resp = api_client.get(url)
    result = resp.json()
    assert resp.status_code == HTTP_200_OK
    assert result['id'] == id_for_view


@pytest.mark.django_db
def test_product_review_list(api_client, product_review_factory):
    """Тест на вывод списка отзывов"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    resp = api_client.get(url)
    result = resp.json()
    expected_ids = {review.id for review in product_reviews}
    result_ids = {review['id'] for review in result}
    assert resp.status_code == HTTP_200_OK
    assert expected_ids == result_ids


@pytest.mark.django_db
def test_product_review_create(api_client, product_factory, ):
    """Тест на создание отзыва, невозможность создания второго отзыва на один и то же товар,
     и невозможность создания отзыва неавторизованным пользователем """
    url = reverse('product-reviews-list')
    product = product_factory()
    product_for_review = product.id
    payload = {
        'product_id': product_for_review,
        'review': 'test review',
        'grade': 3
    }
    resp_not_authenticate = api_client.post(url, payload, format='json')
    test_user = User.objects.create_user('test_user')
    api_client.force_authenticate(user=test_user)
    resp = api_client.post(url, payload, format='json')
    resp2 = api_client.post(url, payload, format='json')
    api_client.force_authenticate(user=None)
    assert resp_not_authenticate.status_code == HTTP_401_UNAUTHORIZED
    assert resp.status_code == HTTP_201_CREATED
    assert resp2.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_product_review_update(api_client, product_review_factory):
    """Тест на изменение/удаление отзыва автором и
     невозможность изменения/удаления другим пользователем"""
    review = product_review_factory()
    id_for_update = review.id
    url = reverse('product-reviews-detail', args=(id_for_update,))
    payload = {
        'product_id': review.product.id,
        'review': 'test review text',
        'grade': 3
    }
    test_user_owner = review.user
    test_user_not_owner = User.objects.create_user('test_user_not_owner',)
    api_client.force_authenticate(user=test_user_not_owner)
    resp_not_owner = api_client.put(url, payload, format='json')
    destroy_not_owner = api_client.delete(url, format='json')
    api_client.force_authenticate(user=test_user_owner)
    resp_owner = api_client.put(url, payload, format='json')
    destroy_owner = api_client.delete(url, format='json')
    assert resp_not_owner.status_code == HTTP_403_FORBIDDEN
    assert destroy_not_owner.status_code == HTTP_403_FORBIDDEN
    assert resp_owner.status_code == HTTP_200_OK
    assert destroy_owner.status_code == HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_review_filter_user(api_client, product_review_factory):
    """Тест фильтра списка отзывов по id пользователя"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    users_id = [review.user.id for review in product_reviews]
    id_for_test = users_id[2]
    resp = api_client.get(url, {'user': id_for_test})
    result = resp.json()
    result_user_ids = {review['user']['id'] for review in result}
    assert resp.status_code == HTTP_200_OK
    assert {id_for_test} == result_user_ids


@pytest.mark.django_db
def test_product_review_filter_product(api_client, product_review_factory):
    """Тест фильтра списка отзывов по id товара"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    products_ids = [review.product.id for review in product_reviews]
    id_for_test = products_ids[2]
    resp = api_client.get(url, {'product': id_for_test})
    result = resp.json()
    result_product_ids = {review['product']['id'] for review in result}
    assert resp.status_code == HTTP_200_OK
    assert {id_for_test} == result_product_ids
