import typing

from appboot.schema import ModelSchemaT


class Service(typing.Generic[ModelSchemaT]):
    schema_class: type[ModelSchemaT]

    def __init__(self, schema: type[ModelSchemaT]) -> None:
        self.schema_class = schema

    async def list(self) -> list[ModelSchemaT]:
        return await self.schema_class.objects.all()

    async def create(self, request: ModelSchemaT) -> ModelSchemaT:
        assert isinstance(request, self.schema_class)
        return await request.save(flush=True)

    async def get(self, pk: int):
        return await self.schema_class.objects.get(pk)

    async def update(self, request: ModelSchemaT) -> ModelSchemaT:
        assert isinstance(request, self.schema_class)
        if request.id:
            raise ValueError()
        return await request.save()

    async def delete(self, pk: int) -> ModelSchemaT:
        obj = await self.schema_class.objects.get(pk)
        if obj is None:
            raise ValueError()
        return await obj.delete()
