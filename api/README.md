# AW40-hub-docker - API

## Overview

A [FastAPI](https://fastapi.tiangolo.com/) application to interact with Hub
ressources.



## Contribute
*(All commands run from repository root)*

### Set up python development environment


Assuming [virtualenv](https://virtualenv.pypa.io/en/latest/) is installed use
```
virtualenv venv
source venv/bin/activate
```
to set up your environment and install requirements for the api package plus
additional requirements for linting and testing via
```
pip install -r requirements.txt
```

### Directory structure

[./api](./api) contains the actual API source code and [./tests](./tests)
the respective tests.

### Tests and code checks

Test via
```
pytest ./api
```
and check code via
```
flake8 ./api
```


