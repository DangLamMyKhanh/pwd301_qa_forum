import pytest
from app import app

@pytest.fixture
def client():
    """Pytest fixture cung cấp Flask test client"""
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def app_ctx():
    """Pytest fixture cung cấp Application Context"""
    with app.app_context():
        yield

