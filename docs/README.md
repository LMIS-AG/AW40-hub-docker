# AW40-hub-docker - Docs


## Development

Install [MkDocs](https://www.mkdocs.org/) via
```
pip install mkdocs
```

From the repo root run mkdocs dev server via
```
mkdocs serve -f docs/de/mkdocs.yml -a 127.0.0.1:8001
```
Note that the non-default port 8001 is suggest to avoid conflicts with the
[api](../api) service.

Now access the docs on http://127.0.0.1:8001

## Deployment

### With Docker

Documentation [Dockerfile](Dockerfile) builds the static website and serves
it with nginx.