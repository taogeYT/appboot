from appboot.apps import BaseAppConfig


class PollsConfig(BaseAppConfig):
    name: str = 'polls'

    class Config:
        env_prefix = 'polls_'


config = PollsConfig()
