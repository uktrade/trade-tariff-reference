from django.test import TestCase, TransactionTestCase


def pytest_sessionstart(session):
    databases_to_enable = {'default', 'tariff'}
    TransactionTestCase.databases = databases_to_enable
    TestCase.databases = databases_to_enable
