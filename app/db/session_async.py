from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.session import Base # Importando Base existente para compartilhar Models

# URL para Async (note o +aiosqlite)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, # Necessário para SQLite
    echo=False
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
