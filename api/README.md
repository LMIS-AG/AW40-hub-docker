# AW40-hub-docker - API

## Overview

A [FastAPI](https://fastapi.tiangolo.com/) application to interact with Hub
ressources.  




## Contribute
*(All commands run from repository root)*

### 1. Set up python development environment


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

### 2. Code

[./api](./api) contains the actual API source code and [./tests](./tests)
the respective tests.

Some suggestions to keep things clean:
- Write tests.
- Adhere to [PEP 8](https://peps.python.org/pep-0008/)
(e.g. just do what flake8 tells you to do).
- Environment variables are read in one place only:
[`api.settings.Settings`](./api/settings.py)
- All configuration specified through environment variables is resolved in the
main entrypoint of the api, which is [`api.main`](./api/main.py). E.g.
`from .settings import settings` happens only in
[`api.main`](./api/main.py) which creates and injects all dependencies
for lower level code.

### 3. Run tests and check code style

Before a commit test via
```
pytest ./api
```
and check code via
```
flake8 ./api
```


