from appboot.apps import BaseAppConfig, BaseSettings


class PollsConfig(BaseAppConfig):
    class Config(BaseSettings.Config):
        env_prefix = 'polls_'

    name: str = 'polls'


config = PollsConfig()
