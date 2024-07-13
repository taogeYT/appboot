import typing

from pydantic import BaseModel

from appboot._compat import PYDANTIC_V2


def make_model_by_obj(model: type[BaseModel], obj: typing.Any) -> BaseModel:
    if PYDANTIC_V2:
        return model.model_validate(obj)
    else:
        return model.parse_obj(obj)
