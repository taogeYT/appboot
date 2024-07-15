from pydantic import BaseModel


class AppConfig(BaseModel):
    name: str
