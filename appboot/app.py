from conf.pydantic_settings import BaseSettings


class BaseAppConfig(BaseSettings):
    name: str

    def ready(self):
        pass
