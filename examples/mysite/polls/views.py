# Create your api here.
from fastapi import APIRouter, Depends

from appboot import PaginationResult, QueryDepends
from appboot.db import create_tables
from polls.models import Choice, Question
from polls.schema import ChoiceSchema, QuestionQuerySchema, QuestionSchema

router = APIRouter(dependencies=[Depends(create_tables)])


@router.post('/questions/', response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    instance = await question.create()
    # await instance.refresh(['choices']) # 有 back_populates 参数会自动加载关联关系
    return instance


@router.get('/questions/', response_model=PaginationResult[QuestionSchema])
async def query_questions(query: QuestionQuerySchema = QueryDepends()):
    return await Question.objects.paginate(query)


@router.get('/questions/{pk}', response_model=QuestionSchema)
async def get_question(pk: int):
    return await Question.objects.get(id=pk)


@router.put('/questions/{pk}', response_model=QuestionSchema)
async def update_question(pk: int, question: QuestionSchema):
    instance = await Question.objects.get(id=pk)
    return await question.update(instance)


@router.delete('/questions/{pk}', response_model=QuestionSchema)
async def delete_question(pk: int):
    instance = await Question.objects.get(id=pk)
    await instance.delete()
    return instance


@router.post('/choices/', response_model=ChoiceSchema)
async def create_choice(choice: ChoiceSchema):
    return await choice.create()


@router.put('/choices/{pk}/vote', response_model=ChoiceSchema)
async def update_choice(pk: int):
    instance = await Choice.objects.get(id=pk)
    instance.votes += 1
    await instance.save()
    return instance
