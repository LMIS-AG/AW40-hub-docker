from pydantic import BaseSettings


class Settings(BaseSettings):
    hub_api_base_url: str = "http://api:8000/v1"
    hub_api_host_url: str = "http://127.0.0.1:8000/v1"

    keycloak_url: str = "http://keycloak:8080"
    keycloak_workshop_realm: str = "workshops"
    keycloak_client_id: str = "demo-ui"
    keycloak_client_secret: str = None

    session_secret: str = "demo-ui-session-secret"


settings = Settings()
