from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user_in: UserCreate) -> User:
        # 1. Verificar se o usuário já existe
        user_exists = await self.repository.get_by_email(user_in.email)
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este e-mail já está cadastrado."
            )

        # 2. Preparar dados (Hash de senha)
        user_data = user_in.model_dump()
        password = user_data.pop("password")
        user_data["hashed_password"] = password + "not-secure-hash"
        
        # 3. Persistir usando o repositório
        return await self.repository.create(user_data)

    async def get_user(self, user_id: int) -> User:
        user = await self.repository.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )
        return user

    async def get_users(self, skip: int = 0, limit: int = 100, **filters):
        return await self.repository.get_all(skip=skip, limit=limit, **filters)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        # Garante que usuario existe
        user = await self.get_user(user_id)

        # Valida duplicidade de email se estiver mudando
        if user_in.email is not None and user_in.email != user.email:
            user_exists = await self.repository.get_by_email(user_in.email)
            if user_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Este e-mail já está cadastrado."
                )

        # Prepara dados de update
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            password = update_data.pop("password")
            update_data["hashed_password"] = password + "not-secure-hash"

        # Atualiza via repo
        return await self.repository.update(user_id, update_data)

    async def delete_user(self, user_id: int) -> None:
        deleted = await self.repository.delete(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )