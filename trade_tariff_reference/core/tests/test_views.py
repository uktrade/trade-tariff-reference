import os

from django.conf import settings
from django.shortcuts import reverse

import pytest


@pytest.mark.django_db
def test_homepage_view(authenticated_client):
    response = authenticated_client.get(reverse('core:homepage'))
    assert response.status_code == 200
    assert 'core/index.html' in [template.name for template in response.templates]
    expected_page_title = '<h1 class="govuk-heading-xl govuk-!-margin-bottom-6">Generate reference documents</h1>'
    assert expected_page_title in str(response.content)


@pytest.mark.django_db
def test_homepage_view_with_unauthorised_user(client):
    response = client.get(reverse('core:homepage'), follow=True)
    assert response.status_code == 404
    assert len(response.redirect_chain) == 2
    assert response.redirect_chain[0] == (reverse('authbroker:login'), 302)
    assert response.redirect_chain[1][0].startswith(
        os.path.join(settings.AUTHBROKER_URL, 'o/authorize/?response_type=code')
    )
    assert response.redirect_chain[1][1] == 302


@pytest.mark.django_db
def test_healthcheck_view(authenticated_client):
    response = authenticated_client.get(reverse('core:health-check'))
    assert response.status_code == 200
    assert 'core/healthcheck.html' in [template.name for template in response.templates]
    assert '<status>OK</status>' in str(response.content)
