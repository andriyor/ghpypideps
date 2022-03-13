# ghpypideps

The goal of this tool is to get as much as possible dependencies that used in python package (including test, dev, doc dependencies)

## Dependencies received from several sources 

- requirements files
- setup.cfg
- setup.py (AST parsing)
- pypi API
- GitHub search

## Example

For Flask

```json
{
  "requirements/dev.txt": [
    "cfgv==3.3.1",
    "click==8.0.3",
    "distlib==0.3.4",
    "filelock==3.4.2",
    "greenlet==1.1.2 ; python_version < \"3.11\"",
    "identify==2.4.8",
    "nodeenv==1.6.0",
    "pep517==0.12.0",
    "pip-compile-multi==2.4.3",
    "pip-tools==6.5.1",
    "platformdirs==2.4.1",
    "pre-commit==2.17.0",
    "pyyaml==6.0",
    "six==1.16.0",
    "toml==0.10.2",
    "toposort==1.7",
    "tox==3.24.5",
    "virtualenv==20.13.1",
    "wheel==0.37.1"
  ],
  "requirements/docs.txt": [
    "alabaster==0.7.12",
    "babel==2.9.1",
    "certifi==2021.10.8",
    "charset-normalizer==2.0.11",
    "docutils==0.16",
    "idna==3.3",
    "imagesize==1.3.0",
    "jinja2==3.0.3",
    "markupsafe==2.0.1",
    "packaging==21.3",
    "pallets-sphinx-themes==2.0.2",
    "pygments==2.11.2",
    "pyparsing==3.0.7",
    "pytz==2021.3",
    "requests==2.27.1",
    "snowballstemmer==2.2.0",
    "sphinx==4.4.0",
    "sphinx-issues==3.0.1",
    "sphinx-tabs==3.2.0",
    "sphinxcontrib-applehelp==1.0.2",
    "sphinxcontrib-devhelp==1.0.2",
    "sphinxcontrib-htmlhelp==2.0.0",
    "sphinxcontrib-jsmath==1.0.1",
    "sphinxcontrib-log-cabinet==1.0.1",
    "sphinxcontrib-qthelp==1.0.3",
    "sphinxcontrib-serializinghtml==1.1.5",
    "urllib3==1.26.8"
  ],
  "requirements/tests-pallets-dev.txt": [
    "click @ https://github.com/pallets/click/archive/refs/heads/main.tar.gz",
    "itsdangerous @ https://github.com/pallets/itsdangerous/archive/refs/heads/main.tar.gz",
    "jinja2 @ https://github.com/pallets/jinja/archive/refs/heads/main.tar.gz",
    "markupsafe @ https://github.com/pallets/markupsafe/archive/refs/heads/main.tar.gz",
    "werkzeug @ https://github.com/pallets/werkzeug/archive/refs/heads/main.tar.gz"
  ],
  "requirements/tests-pallets-min.txt": [
    "click==8.0.0",
    "itsdangerous==2.0.0",
    "jinja2==3.0.0",
    "markupsafe==2.0.0",
    "werkzeug==2.0.0"
  ],
  "requirements/tests.txt": [
    "asgiref==3.5.0",
    "attrs==21.4.0",
    "blinker==1.4",
    "greenlet==1.1.2 ; python_version < \"3.11\"",
    "iniconfig==1.1.1",
    "packaging==21.3",
    "pluggy==1.0.0",
    "py==1.11.0",
    "pyparsing==3.0.7",
    "pytest==7.0.0",
    "python-dotenv==0.19.2",
    "tomli==2.0.1"
  ],
  "requirements/typing.txt": [
    "cffi==1.15.0",
    "cryptography==36.0.1",
    "mypy==0.931",
    "mypy-extensions==0.4.3",
    "pycparser==2.21",
    "tomli==2.0.1",
    "types-contextvars==2.4.2",
    "types-dataclasses==0.6.4",
    "types-setuptools==57.4.9",
    "typing-extensions==4.0.1"
  ],
  "setup.cfg": [],
  "setup.py": [
    "Werkzeug >= 2.0",
    "Jinja2 >= 3.0",
    "itsdangerous >= 2.0",
    "click >= 8.0",
    "importlib-metadata; python_version < '3.10'",
    "asgiref >= 3.2",
    "python-dotenv"
  ],
  "pypi": [
    "Werkzeug (>=2.0)",
    "Jinja2 (>=3.0)",
    "itsdangerous (>=2.0)",
    "click (>=7.1.2)",
    "asgiref (>=3.2) ; extra == 'async'",
    "python-dotenv ; extra == 'dotenv'"
  ]
}
```

## Development setup

Using [Poetry](https://poetry.eustace.io/docs/)

```
poetry install
poetry run python ghpypideps/ghpypideps.py
poetry run pytest --ignore=__pypackages__ -vv
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
