import json
import glob

import pytest

from ghpypideps import fetch_deps

root_path = 'tests/results/'


def read(package_name):
    with open(f'{root_path}{package_name}.json') as json_file:
        return json.load(json_file)


def get_packages():
    packages = []
    for path in glob.glob(f'{root_path}*.json'):
        file_name = path.replace(root_path, '').replace('.json', '')
        packages.append(file_name)
    return packages

# for all dumped
# packages = get_packages()

packages = [
    'matplotlib',
    'six',
    'urllib3'
]


@pytest.mark.parametrize("package_name,expected", [(package, read(package)) for package in packages])
def test_fetch_deps(package_name, expected):
    assert fetch_deps(package_name) == expected
