import json

from ghpypideps import fetch_deps


def read(package_name):
    with open(f'tests/results/{package_name}.json') as json_file:
        return json.load(json_file)


def test_answer():
    package_name = 'click'
    expected = read(package_name)
    assert fetch_deps(package_name) == expected
