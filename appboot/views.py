# api view
from typing import ClassVar, Generic, TypeVar

from fastapi import APIRouter

from appboot.models import Model, ModelT
from appboot.pagination import PaginationResult
from appboot.params import QueryDepends, QuerySchema
from appboot.schema import ModelSchema, ModelSchemaT

PK = TypeVar('PK')


class ModelViewSet(Generic[PK, ModelT, ModelSchemaT]):
    pk_type: ClassVar[type[object]] = int
    model_class: ClassVar[type[Model]]
    schema_class = ClassVar[type[ModelSchema]]
    query_schema_class: ClassVar[type[QuerySchema]] = QuerySchema

    async def list(self, query: QuerySchema):
        return await query.query_result(self.model_class.objects.clone())

    async def get(self, pk: PK):
        return await self.model_class.objects.get(pk)

    async def create(self, data: ModelSchemaT):
        return await data.create()

    async def update(self, pk: PK, data: ModelSchemaT):
        instance = await self.model_class.objects.get(pk)
        return await data.update(instance)

    async def delete(self, pk: PK):
        instance = await self.model_class.objects.get(pk)
        return await instance.delete()

    @classmethod
    def as_router(cls, **kwargs):
        router = APIRouter(**kwargs)
        instance = cls()

        @router.get('/', response_model=PaginationResult[cls.schema_class])
        async def list_objects(query: cls.query_schema_class = QueryDepends()):  # type: ignore
            return await instance.list(query)

        @router.post('/', response_model=cls.schema_class)
        async def create_object(data: cls.schema_class):  # type: ignore
            return await instance.create(data)

        @router.get('/pk', response_model=cls.schema_class)
        async def get_object(pk: cls.pk_type):  # type: ignore
            return await instance.get(pk)

        @router.put('/{pk}', response_model=cls.schema_class)
        async def update_object(pk: cls.pk_type, data: cls.schema_class):  # type: ignore
            return await instance.update(pk, data)

        @router.delete('/{pk}', response_model=cls.schema_class)
        async def delete_object(pk: cls.pk_type):  # type: ignore
            return await instance.delete(pk)

        return router
