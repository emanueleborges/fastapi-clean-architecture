from typing import Optional
from sqlalchemy.future import select
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(self.model).filter(self.model.email == email))
        return result.scalars().first()
