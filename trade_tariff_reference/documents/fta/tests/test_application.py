from unittest import mock


from trade_tariff_reference.documents.fta.application import Application


def test_application():
    with mock.patch('trade_tariff_reference.documents.fta.application.Application._get_config') as mock_get_config:
        mock_get_config.return_value = None
        app = Application('israel')

        assert 1 == 2
