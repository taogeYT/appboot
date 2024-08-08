# App Boot
[AppBoot](https://github.com/taogeYT/appboot) 像Django一样使用fastAPI，内置sqlalchemy开箱即用，旨在提供类似 Django 的开发体验。

## 技术栈
- Python 3.9+
- FastAPI
- SQLAlchemy 2.0+
- Pydantic
- Uvicorn
## 快速开始
### 启动新项目
```shell
# 创建项目目录
mkdir mysite
cd mysite
# 创建虚拟环境以在本地隔离包依赖
python3 -m venv env
source env/bin/activate  # Windows 使用 `env\\Scripts\\activate`
# 安装 appboot 和 aiosqlite 到虚拟环境中
pip install appboot aiosqlite
# 使用单个应用程序设置新项目
appboot startproject mysite .  # 注意尾随的 '.' 字符
# 启动服务器，应用运行在 http://127.0.0.1:8000
python manage.py runserver
```
### 新建APP polls
```shell
python manage.py startapp polls
```
### 创建数据库 Model
在 `polls/models.py` 中定义 `Question` 模型。
```python
from datetime import datetime
from sqlalchemy.orm import Mapped
from appboot import models

class Question(models.Model):
    question_text: Mapped[str]
    pub_date: Mapped[datetime]
```
### 创建 Schema
在 `polls/schema.py` 中定义 `QuestionSchema`。
```python
from appboot.schema import ModelSchema
from polls.models import Question

class QuestionSchema(ModelSchema):
    class Meta:
        model = Question
```
### 编写 CRUD API
在 `polls/views.py` 中编写 CRUD API。
```python
from fastapi import APIRouter, Depends
from appboot.db import create_tables
from appboot.params import QuerySchema, QueryDepends, PaginationResult
from polls.models import Question
from polls.schema import QuestionSchema

router = APIRouter(dependencies=[Depends(create_tables)])

@router.post('/questions/', response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    return await question.create()

@router.get('/questions/', response_model=PaginationResult[QuestionSchema])
async def query_questions(query: QuerySchema = QueryDepends()):
    return await query.query_result(Question.objects.clone())

@router.get('/questions/{question_id}', response_model=QuestionSchema)
async def get_question(question_id: int):
    return await Question.objects.get(question_id)

@router.put('/questions/{question_id}', response_model=QuestionSchema)
async def update_question(question_id: int, question: QuestionSchema):
    instance = await Question.objects.get(question_id)
    return await question.update(instance)

@router.delete('/questions/{question_id}', response_model=QuestionSchema)
async def delete_question(question_id: int):
    instance = await Question.objects.get(question_id)
    return await instance.delete()
```
### 配置 API 路由规则
在 `mysite/urls.py` 中配置 API 路由。
```python
from fastapi import APIRouter
from polls.views import router

root_router = APIRouter()
root_router.include_router(router, prefix='/polls', tags=['polls'])
```
### 测试 API
```shell
python manage.py runserver
```
现在可以通过浏览器直接访问我们的 API 文档，URL 为 [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/)。
![API 文档](https://github.com/taogeYT/oss/blob/main/resource/appboot/images/polls.png?raw=true)
### 创建复杂查询的 QuerySchema
在 `polls/schema.py` 中创建 `QuestionQuerySchema` 以进行复杂查询。
```python
from typing import Optional
from appboot.params import QuerySchema
from appboot.filters import EqField, ContainsField

class QuestionQuerySchema(QuerySchema):
    ids: Optional[list[int]] = EqField(None, alias='pk', columns='id')  # 按 ID 列表查询 Question
    question_text: Optional[str] = ContainsField(None)  # question_text 字段模糊查询
```
在 `polls/views.py` 文件中将 `QuerySchema` 替换为 `QuestionQuerySchema`，然后在浏览器中刷新文档页面，你会看到question列表接口增加了两个新的查询参数。
![复杂查询参数](https://github.com/taogeYT/oss/blob/main/resource/appboot/images/query.png?raw=true)

## 尝试示例
访问 [Examples](https://github.com/taogeYT/appboot) 获取更多示例。
