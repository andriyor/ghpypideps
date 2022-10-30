import json

from ghpypideps.ghpypideps import fetch_deps

if __name__ == "__main__":
    # package_name = 'python-dateutil'
    # package_name = 'six'
    # package_name = 'urllib3'
    # package_name = 'PyYAML'
    # package_name = 'numpy'
    # package_name = 'click'
    # package_name = 'botocore'
    # package_name = 'matplotlib'
    # package_name = 'attrs'
    # package_name = 'pyrsistent'
    # package_name = 'jmespath'
    # package_name = 'Jinja2'
    # package_name = 'PyJWT'
    # package_name = 'oauthlib'
    # package_name = 'requests-oauthlib'
    # package_name = 'google-cloud-core'
    # package_name = 'Werkzeug'
    # package_name = 'Flask'
    # package_name = 'scipy'
    # package_name = 'Pillow'
    # package_name = 'pluggy'
    # package_name = 'tqdm'
    # package_name = 'GitPython'
    # package_name = 'gunicorn'
    # package_name = 'PyNaCl'
    # package_name = 'requests'
    # package_name = 's3transfer'
    # package_name = 'idna'
    # package_name = 'chardet'
    # package_name = 'pyasn1'
    # package_name = 'futures'
    # package_name = 'setuptools'
    # package_name = 'google-cloud-core'
    # package_name = 'colorama'
    # package_name = 'simplejson'
    # package_name = 'boto3'
    # package_name = 'wheel'
    package_name = 'protobuf'

    deps = fetch_deps(package_name)

    print(json.dumps(deps, indent=2))

    with open(f'tests/results/{package_name}.json', 'w') as outfile:
        json.dump(deps, outfile, indent=2)
