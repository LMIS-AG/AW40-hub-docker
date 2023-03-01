from fastapi import FastAPI

from .v1 import api_v1

app = FastAPI()

app.mount("/v1", api_v1)
