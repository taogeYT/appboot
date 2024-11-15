# Create your api here.
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import joinedload
from starlette import status

from appboot import PaginationResult, QueryDepends, QuerySchema
from appboot.db import create_tables
from chat.schema import Message, MessageSchema, User, UserLogin, UserSchema

router = APIRouter(dependencies=[Depends(create_tables)])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token.startswith('simple_token_'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return token.strip('simple_token_')


@router.post('/login')
async def login(data: UserLogin):
    user = await User.objects.filter_by(
        username=data.username, password=data.password
    ).first()
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    return {'token': f'simple_token_{user.id}'}


@router.post('/users/', response_model=UserSchema)
async def create_user(user: UserSchema):
    return await user.create()


@router.get('/users/', response_model=PaginationResult[UserSchema])
async def query_users(query: QuerySchema = QueryDepends()):
    return await User.objects.filter_query(query).all()


@router.post('/messages/', response_model=MessageSchema)
async def create_message(data: MessageSchema, user_id: int = Depends(get_current_user)):
    msg = await data.create(user_id=user_id)
    return await msg.refresh(['user'])


@router.get('/messages/', response_model=PaginationResult[MessageSchema])
async def query_messages(query: QuerySchema = QueryDepends()):
    return (
        await Message.objects.options(joinedload(Message.user))
        .filter_query(query)
        .all()
    )
