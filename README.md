# ghpypideps

The goal of this tool is to get as much as possible dependencies that used in python package (including test, dev, doc dependencies)

```
poetry install
poetry run python ghpypideps/ghpypideps.py
poetry run pytest --ignore=__pypackages__ -vv
```
