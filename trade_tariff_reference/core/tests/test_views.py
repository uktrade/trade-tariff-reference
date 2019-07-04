import pytest


@pytest.mark.django_db
def test_homepage_view(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "Hello" in str(response.content)
