import re
import secrets
import typing

from pydantic import BaseModel

from appboot._compat import PYDANTIC_V2


def make_model_by_obj(model: type[BaseModel], obj: typing.Any) -> BaseModel:
    if PYDANTIC_V2:
        return model.model_validate(obj)
    else:
        return model.parse_obj(obj)


def snake_to_camel(snake_str: str) -> str:
    """
    :param snake_str: app_boot
    :return: appBoot
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def snake_to_pascal(snake_str: str) -> str:
    """
    :param snake_str: app_boot
    :return: AppBoot
    """
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


def camel_to_snake(name: str) -> str:
    """
    :param name: AppBoot
    :return: app_boot
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_random_secret_key():
    """
    Return a 50 character random string usable as a SECRET_KEY setting value.
    """
    return secrets.token_hex(32)
