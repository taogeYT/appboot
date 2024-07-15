# import typing
#
# from fastapi import APIRouter
#
# from appboot.services import Service
#
#
# class FastAPIRouter(APIRouter):
#     def register(
#         self,
#         prefix: str,
#         service: Service,
#         method: typing.Sequence[str] = ("create", "list", "get", "update", "delete"),
#     ):
#         if not prefix.startswith("/"):
#             prefix = "/" + prefix
#         if "create" in method:
#
#             @self.post(prefix + "/", response_model=service.schema_class)
#             async def create(data: service.schema_class.create_schema):
#                 request = service.schema_class.model_validate(data)
#                 return await service.create(request)
#
#         if "update" in method:
#
#             @self.put(prefix + "/{pk}", response_model=service.schema_class)
#             async def update(
#                 pk: int, data: service.schema_class.make_update_schema()
#             ) -> service.schema_class:
#                 request = service.schema_class.model_validate(data)
#                 request.id = pk
#                 return await service.update(request)
#
#         if "list" in method:
#
#             @self.get(prefix + "/", response_model=list[service.schema_class])
#             async def get_list():
#                 return await service.list()
#
#         if "get" in method:
#
#             @self.get(prefix + "/{pk}", response_model=service.schema_class)
#             async def get(pk: int) -> service.schema_class:
#                 return await service.get(pk)
#
#         if "delete" in method:
#
#             @self.delete(prefix + "/{pk}", response_model=service.schema_class)
#             async def delete(pk: int) -> service.schema_class:
#                 return await service.delete(pk)
