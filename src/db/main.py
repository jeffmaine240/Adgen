from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker


from src.config import Config

print(Config.DATABASE_URL)

engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        echo=True
    )
)

Session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession: # type: ignore
    async with Session() as session:
        yield session