import importlib
import os
import typing
import warnings

from appboot._compat import PydanticModelMetaclass
from appboot.conf.default import DefaultSettings

ENVIRONMENT_VARIABLE = "APP_BOOT_SETTINGS_MODULE"


def _parse_field_from_mod(mod, attrs):
    attrs.update({name: getattr(mod, name) for name in mod.__annotations__})
    if "__annotations__" in attrs:
        attrs["__annotations__"].update(mod.__annotations__)
    else:
        attrs["__annotations__"] = mod.__annotations__


class BaseSettingsMetaclass(PydanticModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: tuple[type[typing.Any], ...],
        namespace: dict[str, typing.Any],
        **kwargs: typing.Any,
    ) -> type:
        meta = namespace["Meta"]
        settings_module = getattr(meta, "settings_module", None)
        if settings_module:
            mod = importlib.import_module(settings_module)
            _parse_field_from_mod(mod, namespace)
        else:
            warnings.warn("settings_module are not configured")
        new_cls = super().__new__(mcs, cls_name, bases, namespace, **kwargs)
        return new_cls


class Settings(DefaultSettings, metaclass=BaseSettingsMetaclass):
    """
    os.environ.setdefault('APP_BOOT_SETTINGS_MODULE', 'myapp.settings')
    """

    class Meta:
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)


class LazySettings:
    def __init__(self):
        self._wrapped = None

    def __getattr__(self, name):
        if self._wrapped is None:
            self._wrapped = Settings()
        val = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val


settings = LazySettings()
