from appboot.apps import BaseAppConfig, BaseSettings


class ChatConfig(BaseAppConfig):
    class Config(BaseSettings.Config):
        env_prefix = 'chat_'

    name: str = 'chat'


config = ChatConfig()
