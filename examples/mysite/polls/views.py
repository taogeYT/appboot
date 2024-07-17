# Create your api here.
from fastapi import APIRouter, Depends

from appboot import Model
from appboot.db import engine
from polls.models import Question
from polls.schema import QuestionSchema


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


router = APIRouter(
    prefix="/polls", tags=["polls"], dependencies=[Depends(create_tables)]
)


@router.post("/questions/", response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    return await Question.objects.create(question, flush=True)


@router.get("/questions/", response_model=list[QuestionSchema])
async def query_questions(limit: int = 10, offset: int = 0):
    return await Question.objects.limit(limit).offset(offset).all()


@router.get("/questions/{question_id}", response_model=QuestionSchema)
async def get_question(question_id: int):
    return await Question.objects.get(question_id)


@router.put("/questions/{question_id}", response_model=QuestionSchema)
async def update_question(question_id: int, question: QuestionSchema):
    return await Question.objects.update(question_id, question)


@router.delete("/questions/{question_id}", response_model=QuestionSchema)
async def delete_question(question_id: int):
    return await Question.objects.delete(question_id, flush=True)
