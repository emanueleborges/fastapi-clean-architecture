from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.service.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.db.session_async import get_db

router = APIRouter()

# Dependency para instanciar o Service com o Repository correto
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repository = UserRepository(User, db)
    return UserService(repository)

@router.post("/", response_model=UserResponse)
async def register_user(
    user_in: UserCreate, 
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(user_in)


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0, 
    limit: int = 100, 
    is_active: Optional[bool] = Query(None, description="Filtrar por status de ativação"),
    service: UserService = Depends(get_user_service)
):
    return await service.get_users(skip=skip, limit=limit, is_active=is_active)


@router.get("/{user_id}", response_model=UserResponse)
async def retrieve_user(
    user_id: int, 
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def edit_user(
    user_id: int, 
    user_in: UserUpdate, 
    service: UserService = Depends(get_user_service)
):
    return await service.update_user(user_id, user_in)


@router.delete("/{user_id}", status_code=204)
async def remove_user(
    user_id: int, 
    service: UserService = Depends(get_user_service)
):
    await service.delete_user(user_id)