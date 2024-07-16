# Create your api here.
from fastapi import APIRouter, Depends

from appboot import Model
from appboot.db import engine, transaction
from polls.models import Question
from polls.schema import QuestionSchema


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def get_session():
    await create_tables()
    async with transaction() as session:
        yield session


router = APIRouter(prefix="/polls", tags=["polls"], dependencies=[Depends(get_session)])


@router.post("/questions/", response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    r = await Question.objects.create(question, flush=True)
    return r


@router.get("/questions/", response_model=list[QuestionSchema])
async def read_questions():
    return await Question.objects.all()


@router.get("/questions/{question_id}", response_model=QuestionSchema)
async def read_question(question_id: int):
    obj = await Question.objects.get(question_id)
    if obj is None:
        raise ValueError("Question not found")
    return


@router.put("/questions/{question_id}", response_model=QuestionSchema)
async def update_question(question_id: int, question: QuestionSchema):
    obj = await Question.objects.update(question_id, question)
    return obj


@router.delete("/questions/{question_id}", response_model=QuestionSchema)
async def delete_question(question_id: int):
    obj = await Question.objects.get(question_id)
    if obj is None:
        raise ValueError("Question not found")
    obj.delete()
    return obj
