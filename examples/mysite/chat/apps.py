from appboot.apps import BaseAppConfig


class ChatConfig(BaseAppConfig):
    name: str = 'chat'

    class Config:
        env_prefix = 'chat_'


config = ChatConfig()
