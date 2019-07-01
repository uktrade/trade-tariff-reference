import pytest


@pytest.mark.django_db
def test_homepage_view(rf):
    response = rf.get('/')
    assert response.status_code == 213


def test_homepage_2():
    assert 1 == 2
