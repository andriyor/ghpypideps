import json

from ghpypideps import fetch_deps


def read(package_name):
    with open(f'tests/results/{package_name}.json') as json_file:
        return json.load(json_file)


# TODO: parametrize tests

def test_click():
    package_name = 'click'
    expected = read(package_name)
    assert fetch_deps(package_name) == expected


def test_botocore():
    package_name = 'botocore'
    expected = read(package_name)
    assert fetch_deps(package_name) == expected


def test_urllib3():
    package_name = 'urllib3'
    expected = read(package_name)
    assert fetch_deps(package_name) == expected
