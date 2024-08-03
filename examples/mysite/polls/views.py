# Create your api here.
from fastapi import APIRouter, Depends

from appboot import PaginationResult, QueryDepends
from appboot.db import create_tables
from polls.models import Question
from polls.schema import QuestionQuerySchema, QuestionSchema

router = APIRouter(dependencies=[Depends(create_tables)])


@router.post('/questions/', response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    return await question.create()


@router.get('/questions/', response_model=PaginationResult[QuestionSchema])
async def query_questions(query: QuestionQuerySchema = QueryDepends()):
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


@router.post('/questions/{question_text}', response_model=int)
async def bulk_update_question(question_text: str, question: QuestionSchema):
    return await Question.objects.filter_by(question_text=question_text).update(
        question
    )
