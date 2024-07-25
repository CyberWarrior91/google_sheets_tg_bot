import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import os
from .models import Base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = URL.create(
    "postgresql+asyncpg",
    username=os.environ.get('PSQL_LOGIN'),
    password=os.environ.get('PSQL_PASS'),
    host=os.environ.get('PSQL_HOST'),
    port=os.environ.get('PSQL_PORT'),
    database=os.environ.get('PSQL_DB_NAME'),
)

# async def create_tables():
#     engine = create_async_engine(DATABASE_URL)
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#         print("Tables created successfully.")
#     await engine.dispose()


async def get_async_session():
  """
  Asynchronously creates and returns a SQLAlchemy session object.

  Returns:
    An SQLAlchemy session object.
  """
  engine = create_async_engine(DATABASE_URL)
  async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  
  async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

  async with async_session() as session:
    try:
        yield session
    except Exception as e:
        print(e)
        await session.rollback()
    finally:
        await session.close()
  await engine.dispose()
