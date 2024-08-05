from appboot.conf import BaseSettings


class BaseAppConfig(BaseSettings):
    name: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'

    def ready(self):
        pass
