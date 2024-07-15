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
    :param snake_str: app_name
    :return: appName
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def snake_to_pascal(snake_str: str) -> str:
    """
    :param snake_str: app_name
    :return: AppName
    """
    components = snake_str.split("_")
    return "".join(x.title() for x in components)
