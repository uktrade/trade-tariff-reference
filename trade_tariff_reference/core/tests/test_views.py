import pytest
from django.shortcuts import reverse


@pytest.mark.django_db
def test_homepage_view(client):
    response = client.get(reverse('core:homepage'))
    assert response.status_code == 200
    assert 'core/index.html' in [template.name for template in response.templates]
    expected_page_title = '<h1 class="govuk-heading-xl govuk-!-margin-bottom-6">Generate reference documents</h1>'
    assert expected_page_title in str(response.content)
