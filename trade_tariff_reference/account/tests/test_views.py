from django.shortcuts import reverse

import pytest


@pytest.mark.django_db
def test_logout_view(authenticated_client):
    response = authenticated_client.get(reverse('core:homepage'))
    assert response.status_code == 200
    assert response.context['request'].user.is_authenticated is True

    logout_response = authenticated_client.get(reverse('account:logout'))
    assert logout_response.status_code == 200
    assert logout_response.context['request'].user.is_authenticated is False

    assert 'account/logout.html' in [template.name for template in logout_response.templates]
    expected_page_title = 'Thanks for visiting you are now logged out.'
    assert expected_page_title in str(logout_response.content)
