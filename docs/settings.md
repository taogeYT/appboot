# Settings
本文将介绍 AppBoot Settings 的工作原理及其使用方式。
## 原理说明
虽然 AppBoot Settings 的设计与 Django settings 相似，但它的实现方式有明显的不同。你可以将整个 `settings.py` 模块理解为 `pydantic-settings` 的一个配置类。因此，在 AppBoot 项目中，配置 `settings.py` 文件时，必须为每个配置变量明确指定类型注解，否则设置将无法生效。只有明确定义了类型注解，`pydantic-settings` 才能正确解析配置，从而更好地与 `mypy` 结合，帮助构建规范且稳定的 Python 项目。
## 内置默认配置项介绍
```python
from appboot.conf import DataBases, DictConfig
PROJECT_NAME: str = ''  # 项目名称
USE_TZ: bool = True  # 是否使用时区
TIME_ZONE: str = 'Asia/Shanghai'  # 时区配置
DATABASES: DataBases = DataBases(default=dict(url='sqlite+aiosqlite:///:memory:'))  # 数据库配置
FASTAPI: DictConfig = {}  # FastAPI 应用初始化参数配置
ALLOWED_HOSTS: list[str] = ['*']  # 允许的跨站请求域名，默认所有域名都允许
ROOT_URLCONF: str = ''  # 项目路由配置文件
DEFAULT_TABLE_NAME_PREFIX: str = ''  # 全局数据表名称前缀配置
```
## 如何覆盖不同环境下的配置项
由于 AppBoot 是通过 `pydantic-settings` 实现的，因此天然支持通过环境变量或配置文件加载设置。详细使用方法可以参考 [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) 文档。

配置覆盖的优先级如下：

`settings.py < 文件配置 < 环境变量配置`
例如，配置数据库连接如下：
```python
from appboot.conf import DataBases
DATABASES: DataBases = DataBases(
    default=dict(url=f'sqlite+aiosqlite:///db.sqlite3')
)
```
可以通过设置以下环境变量来覆盖数据库配置：
```shell
# 设置环境变量
export DATABASES='{"default": {"url": "sqlite+aiosqlite:///environment.sqlite3"}}'
```
或者使用嵌套属性：
```shell
# 设置环境变量
export DATABASES__default__url='sqlite+aiosqlite:///environment.sqlite3'
```
这两种方式都可以覆盖 `settings.py` 中的默认配置，因为环境变量的优先级最高。此外，AppBoot 默认支持从 `.env` 文件中加载配置。
