
def assert_xml(actual, expected):
    actual = actual.replace('\n    ', '')
    actual = actual.replace('\n  ', '')
    actual = actual.replace('\n', '')
    assert actual == expected
