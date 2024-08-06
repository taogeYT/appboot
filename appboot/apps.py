from appboot.conf import BaseSettings


class BaseAppConfig(BaseSettings):
    name: str

    def ready(self):
        pass
