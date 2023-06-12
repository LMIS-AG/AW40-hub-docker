from pydantic import BaseSettings


class Settings(BaseSettings):
    api_allow_origins: str
    mongo_host: str
    mongo_username: str
    mongo_password: str
    mongo_db: str

    @property
    def mongo_uri(self):
        username = self.mongo_username
        password = self.mongo_password
        host = self.mongo_host

        return f"mongodb://{username}:{password}" \
               f"@{host}:27017/?authSource=admin"
    
    @property
    def allowed_origins(self):
        return [x for x in self.api_allow_origins.split(',') if x]


settings = Settings()
