# Register your schema here.
import typing

from appboot import ModelSchema, Schema
from chat.models import Message, User


class UserLogin(Schema):
    username: str
    password: str


class UserSchema(ModelSchema):
    class Meta:
        model = User
        read_only_fields = ('created_at', 'updated_at')


class MessageSchema(ModelSchema):
    user: typing.Optional[UserSchema] = None

    class Meta:
        model = Message
        read_only_fields = ('user_id', 'created_at', 'updated_at', 'user')
