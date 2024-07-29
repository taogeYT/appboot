# Create your api here.
from fastapi import APIRouter, Depends

from appboot.db import create_tables
from appboot.params import PaginationResult, QueryDepends
from polls.models import Question
from polls.schema import QuestionQuerySchema, QuestionSchema

router = APIRouter(
    prefix='/polls', tags=['polls'], dependencies=[Depends(create_tables)]
)


@router.post('/questions/', response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    return await Question.objects.create(question, flush=True)


@router.get('/questions/', response_model=PaginationResult[QuestionSchema])
async def query_questions(query: QuestionQuerySchema = QueryDepends()):
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
