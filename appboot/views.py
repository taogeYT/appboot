# api view
from typing import ClassVar, Generic

from appboot.models import Model, ModelT
from appboot.params import QuerySchema
from appboot.schema import ModelSchema, ModelSchemaT


class ModelView(Generic[ModelT, ModelSchemaT]):
    model_class: ClassVar[type[Model]]
    schema_class = ClassVar[type[ModelSchema]]
    query_schema_class: ClassVar[type[QuerySchema]] = QuerySchema

    async def list(self, query: QuerySchema):
        return await query.query_result(self.model_class.objects.clone())

    async def get(self, question_id: int):
        return await self.model_class.objects.get(question_id)

    async def create(self, question: ModelSchemaT):
        return await self.model_class.objects.create(question, flush=True)

    async def update(self, question_id: int, question: ModelSchemaT):
        return await self.model_class.objects.update_one(question_id, question)

    async def delete(self, question_id: int):
        return await self.model_class.objects.delete_one(question_id, flush=True)
