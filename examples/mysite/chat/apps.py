from appboot.apps import AppConfig as AppConfigBase


class ChatConfig(AppConfigBase):
    name: str = 'chat'
