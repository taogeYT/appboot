# App Boot
App Boot a FastAPI project template, Designed to provide a Django-like structure and development experience.

# Technology Stack
 - Python 3.9+
 - FastAPI
 - Sqlalchemy2.0+
 - Pydantic
 - uvicorn

# Quick start
Startup up a new project
```shell
# Create the project directory
mkdir mysite
cd mysite

# Create a virtual environment to isolate our package dependencies locally
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Install appboot and aiosqlite into the virtual environment
pip3 install appboot aiosqlite

# Set up a new project with a single application
appboot startproject mysite .  # Note the trailing '.' character

# start runserver Application running on http://127.0.0.1:8000
python3 manage.py runserver
```
Startup up a new app polls
```shell
python3 manage.py startapp polls
```
Create model: define a Question model in polls/models.py.
```python3
from datetime import datetime
from sqlalchemy.orm import Mapped
from appboot import models


class Question(models.Model):
    question_text: Mapped[str]
    pub_date: Mapped[datetime]
```
Create schema: define a Question schema in polls/schema.py.
```python3
from appboot.schema import ModelSchema
from polls.models import Question


class QuestionSchema(ModelSchema):
    class Meta:
        model = Question
```
Write CURD api in polls/views.py
```python3
from fastapi import APIRouter, Depends

from appboot.db import create_tables
from appboot.params import QuerySchema, QueryDepends, PaginationResult
from polls.models import Question
from polls.schema import QuestionSchema


router = APIRouter(
    prefix='/polls', tags=['polls'], dependencies=[Depends(create_tables)]
)

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
Okay, now let's wire up the API URLs. On to mysite/urls.py...
```python3
from fastapi import APIRouter
from polls.views import router
# todo
root_router = APIRouter()
root_router.include_router(router)
```
Testing our API
```shell
python3 manage.py runserver
```
We can now access our API directly through the browser, by going to the URL http://127.0.0.1:8000/docs/...
![](https://raw.githubusercontent.com/taogeYT/appboot/v0.1.7/images/polls.png)

Create QuestionQuerySchema for complex query question in polls/schema.py.
```python3
from typing import Optional
from appboot.params import QuerySchema
from appboot.filters import EqField, ContainsField

class QuestionQuerySchema(QuerySchema):
    ids: Optional[list[int]] = EqField(None, alias='pk', columns='id')  # query question by id list
    question_text: Optional[str] = ContainsField(None)  # fuzzy query question_text
```
Replace QuerySchema with QuestionQuerySchema in the file polls/views.py, refresh docs in browser, You will see two new query param in query questions api
![](https://raw.githubusercontent.com/taogeYT/appboot/v0.1.7/images/query.png)

# Try out examples
Go to [Examples](./examples)
