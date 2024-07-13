from fastapi import Depends, FastAPI

from app_polls.schema import QuestionSchema
from appboot import Model, settings, transaction
from appboot.db import engine


# 创建表
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def get_session():
    async with transaction() as session:
        yield session


app = FastAPI(dependencies=[Depends(get_session)])
print(settings.DATABASES.default)


@app.on_event("startup")
async def on_startup():
    await create_tables()


@app.post("/questions/", response_model=QuestionSchema)
async def create_question(question: QuestionSchema):
    return await question.save()


@app.get("/questions/", response_model=list[QuestionSchema])
async def read_questions(skip: int = 0, limit: int = 10):
    return await QuestionSchema.objects.limit(limit, skip).all()


@app.get("/questions/{question_id}", response_model=QuestionSchema)
async def read_question(question_id: int):
    return await QuestionSchema.objects.get(question_id)


@app.delete("/questions/{question_id}", response_model=QuestionSchema)
async def delete_question(question_id: int):
    obj = await QuestionSchema.objects.get(question_id)
    return await obj.delete()
