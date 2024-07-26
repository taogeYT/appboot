# Create your api here.
from fastapi import APIRouter, Depends

from appboot.db import create_tables
from appboot.filters import FilterDepends
from polls.models import Question
from polls.schema import QuestionFilterSchema, QuestionSchema

router = APIRouter(
    prefix='/polls', tags=['polls'], dependencies=[Depends(create_tables)]
)


@router.post('/questions/', response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    return await Question.objects.create(question, flush=True)


@router.get('/questions/', response_model=list[QuestionSchema])
async def query_questions(query: QuestionFilterSchema = FilterDepends()):
    question_query = Question.objects.all()
    return await query.filter(question_query).get_all()


@router.get('/questions/{question_id}', response_model=QuestionSchema)
async def get_question(question_id: int):
    return await Question.objects.get(question_id)


@router.put('/questions/{question_id}', response_model=QuestionSchema)
async def update_question(question_id: int, question: QuestionSchema):
    return await Question.objects.update(question_id, question)


@router.delete('/questions/{question_id}', response_model=QuestionSchema)
async def delete_question(question_id: int):
    return await Question.objects.delete(question_id, flush=True)
