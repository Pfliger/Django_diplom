import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_factory():
    def factory(**kwargs):
        return baker.make('Product', **kwargs)

    return factory


@pytest.fixture
def product_review_factory():
    def factory(**kwargs):
        return baker.make('ProductReview', **kwargs)

    return factory


@pytest.fixture
def product_collection_factory():
    def factory(**kwargs):
        return baker.make('ProductCollection', **kwargs)

    return factory


@pytest.fixture
def order_factory():
    def factory(**kwargs):
        return baker.make('Order', **kwargs)

    return factory