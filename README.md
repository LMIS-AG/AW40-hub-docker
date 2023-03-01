# AW40-hub-docker

## Overview

Prototype implementation of the AW40 HUB Architecture on Docker\
Currently deployed services:
- Keycloak
- PostgreSQL (Keycloak Database)
- MINIO Object Storage
- MongoDB
- Mongo-Express
- API

## Usage

### Start the developement HUB
**WARNINNG: DO NOT RUN THE DEVELOPEMENT HUB ON PUBLIC SERVER**\
To start the HUB in developer mode use:\
```docker compose --env-file=dev.env up -d```

The interactive docs of the API service can now be accessed via
http://127.0.0.1:8000/v1/docs.

### Stop the HUB
To stop the HUB use:\
```docker compose down``` \
To stop the HUB and **clear all Databases** use:\
```docker compose down -v ```
