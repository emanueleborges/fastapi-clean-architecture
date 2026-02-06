from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        query = select(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, obj_in) -> ModelType:
        # Assume obj_in é um dict ou modelo Pydantic
        obj_data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in) -> Optional[ModelType]:
        db_obj = await self.get(id)
        if not db_obj:
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        db_obj = await self.get(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
            return True
        return False
