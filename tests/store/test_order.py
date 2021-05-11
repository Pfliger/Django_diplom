import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, \
    HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_order_detail(api_client, order_factory):
    """тест на вывод конкретного заказа:
         пользователю только своего заказа, админу любого заказа
         и невозможности получения заказа неавторизованному пользователю"""
    order = order_factory()
    order_id = order.id
    url = reverse('orders-detail', args=(order_id,))
    resp_not_authenticate = api_client.get(url)
    test_user_owner = order.user
    api_client.force_authenticate(user=test_user_owner)
    resp_owner = api_client.get(url)
    test_admin = User.objects.create_user('test_admin', is_staff=True)
    api_client.force_authenticate(user=test_admin)
    resp_admin = api_client.get(url)
    test_user_not_owner = User.objects.create_user('test_not_owner')
    api_client.force_authenticate(user=test_user_not_owner)
    resp_not_owner = api_client.get(url)
    assert resp_not_authenticate.status_code == HTTP_401_UNAUTHORIZED
    assert resp_owner.status_code == HTTP_200_OK
    assert resp_admin.status_code == HTTP_200_OK
    assert resp_not_owner.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_order_list(api_client, order_factory):
    """тест на вывод списка заказов:
     пользователю только своих заказов, админу всего списка, неавторизованному пользователю никаких"""
    orders = order_factory(_quantity=5)
    url = reverse('orders-list')
    resp_not_authenticate = api_client.get(url)
    test_user = orders[3].user
    api_client.force_authenticate(user=test_user)
    resp_test_user = api_client.get(url)
    test_admin = User.objects.create_user('test_admin', is_staff=True)
    api_client.force_authenticate(user=test_admin)
    resp_admin = api_client.get(url)
    assert resp_test_user.status_code == HTTP_200_OK and len(resp_test_user.data) == 1
    assert resp_admin.status_code == HTTP_200_OK and len(resp_admin.data) == 5
    assert resp_not_authenticate.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_order_create(api_client, product_factory):
    """тест на создание заказа авторизованным пользователем и
     невозможность создания неавторизованным пользователем"""
    url = reverse('orders-list')
    product = product_factory()
    payload = {
        "products": [
            {
                "product": product.id,
                "quantity": 10
            }
        ]
    }
    resp_not_authenticate = api_client.post(url, payload, format='json')
    test_user = User.objects.create_user('test_user')
    api_client.force_authenticate(user=test_user)
    resp_test_user = api_client.post(url, payload, format='json')
    assert resp_not_authenticate.status_code == HTTP_401_UNAUTHORIZED
    assert resp_test_user.status_code == HTTP_201_CREATED


@pytest.mark.django_db
def test_order_update(api_client, product_factory, order_factory):
    """тест на изменение пользователем только своего заказа"""
    order = order_factory()
    url = reverse('orders-detail', args=(order.id,))
    product = product_factory()
    payload = {
        "products": [
            {
                "product": product.id,
                "quantity": 5
            }
        ]
    }
    test_user_owner = order.user
    api_client.force_authenticate(user=test_user_owner)
    resp_user_owner = api_client.put(url, payload, format='json')
    test_user_not_owner = User.objects.create_user('test_not_owner')
    api_client.force_authenticate(user=test_user_not_owner)
    resp_not_owner = api_client.put(url, payload, format='json')
    assert resp_not_owner.status_code == HTTP_403_FORBIDDEN
    assert resp_user_owner.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_order_update_status(api_client, order_factory, ):
    """Тест на изменение статуса заказа администратором и невозможность изменения пользователем"""
    order = order_factory()
    url = reverse('orders-detail', args=(order.id,))
    payload = {
        "order_status": "DONE"
    }
    test_user = order.user
    api_client.force_authenticate(user=test_user)
    resp_user = api_client.patch(url, payload, format='json')
    test_admin = User.objects.create_user('test_admin', is_staff=True)
    api_client.force_authenticate(user=test_admin)
    resp_admin = api_client.patch(url, payload, format='json')
    resp_admin_json = resp_admin.json()
    assert resp_user.status_code == HTTP_400_BAD_REQUEST
    assert resp_admin.status_code == HTTP_200_OK and resp_admin_json['order_status'] == 'DONE'


@pytest.mark.django_db
def test_order_filter_status(api_client, order_factory):
    """Тест фильтра по статусу заказа"""
    test_admin = User.objects.create_user('test_admin', is_staff=True)
    order_factory(_quantity=5, order_status='DONE')
    order_factory(_quantity=3, order_status='IN_PROGRESS')
    url = reverse('orders-list')
    api_client.force_authenticate(user=test_admin)
    resp_done = api_client.get(url, {'order_status__iexact': 'DONE'})
    assert resp_done.status_code == HTTP_200_OK
    assert len(resp_done.json()) == 5


@pytest.mark.django_db
def test_order_filter_total(api_client, order_factory, ):
    """Тест фильтра по общей сумме"""
    order_factory(total=float(5000.00))
    order_factory(total=float(3000.00))
    order_factory(total=float(4000.00))

    test_admin = User.objects.create_user('test_user', is_staff=True)
    url = reverse('orders-list')
    api_client.force_authenticate(user=test_admin)
    resp = api_client.get(url, {'total__lte': 4000.00})
    resp_json = resp.json()
    total_list = [float(_['total']) for _ in resp_json]
    assert resp.status_code == HTTP_200_OK
    for amount in total_list:
        assert amount <= 4000.00
