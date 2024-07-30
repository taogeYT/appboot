# App Boot
English | [中文翻译](./README.zh-CN.md)

[AppBoot](https://github.com/taogeYT/appboot) is a FastAPI project template designed to provide a Django-like structure and development experience.
## Technology Stack
- Python 3.9+
- FastAPI
- SQLAlchemy 2.0+
- Pydantic
- Uvicorn
## Quick Start
### Start a New Project
```shell
# Create the project directory
mkdir mysite
cd mysite
# Create a virtual environment to isolate our package dependencies locally
python3 -m venv env
source env/bin/activate  # On Windows use `env\\Scripts\\activate`
# Install appboot and aiosqlite into the virtual environment
pip install appboot aiosqlite
# Set up a new project with a single application
appboot startproject mysite .  # Note the trailing '.' character
# Start the server, application running on http://127.0.0.1:8000
python manage.py runserver
```
### Start a New App 'polls'
```shell
python manage.py startapp polls
```
### Create a Model
Define a `Question` model in `polls/models.py`.
```python
from datetime import datetime
from sqlalchemy.orm import Mapped
from appboot import models

class Question(models.Model):
    question_text: Mapped[str]
    pub_date: Mapped[datetime]
```
### Create a Schema
Define a `Question` schema in `polls/schema.py`.
```python
from appboot.schema import ModelSchema
from polls.models import Question

class QuestionSchema(ModelSchema):
    class Meta:
        model = Question
```
### Write CRUD API
Write the CRUD API in `polls/views.py`.
```python
from fastapi import APIRouter, Depends
from appboot.db import create_tables
from appboot.params import QuerySchema, QueryDepends, PaginationResult
from polls.models import Question
from polls.schema import QuestionSchema

router = APIRouter(dependencies=[Depends(create_tables)])

@router.post('/questions/', response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    return await Question.objects.create(question, flush=True)

@router.get('/questions/', response_model=PaginationResult[QuestionSchema])
async def query_questions(query: QuerySchema = QueryDepends()):
    return await query.query_result(Question.objects.clone())

@router.get('/questions/{question_id}', response_model=QuestionSchema)
async def get_question(question_id: int):
    return await Question.objects.get(question_id)

@router.put('/questions/{question_id}', response_model=QuestionSchema)
async def update_question(question_id: int, question: QuestionSchema):
    return await Question.objects.update_one(question_id, question)

@router.delete('/questions/{question_id}', response_model=QuestionSchema)
async def delete_question(question_id: int):
    return await Question.objects.delete_one(question_id, flush=True)
```
### Configure API Routes
Wire up the API URLs in `mysite/urls.py`.
```python
from fastapi import APIRouter
from polls.views import router

root_router = APIRouter()
root_router.include_router(router, prefix='/polls', tags=['polls'])
```
### Testing Our API
```shell
python manage.py runserver
```
We can now access our API directly through the browser at [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/).
![API Documentation](https://raw.githubusercontent.com/taogeYT/appboot/main/images/polls.png)
### Create Complex Query Schema
Create a `QuestionQuerySchema` for complex queries in `polls/schema.py`.
```python
from typing import Optional
from appboot.params import QuerySchema
from appboot.filters import EqField, ContainsField

class QuestionQuerySchema(QuerySchema):
    ids: Optional[list[int]] = EqField(None, alias='pk', columns='id')  # Query questions by ID list
    question_text: Optional[str] = ContainsField(None)  # Fuzzy query question_text
```
Replace `QuerySchema` with `QuestionQuerySchema` in `polls/views.py`, refresh the docs in the browser, and you will see two new query parameters in the query questions API.
![Complex Query Parameters](https://raw.githubusercontent.com/taogeYT/appboot/main/images/query.png)
## Try Out Examples
Go to [Examples](./examples) for more examples.
