import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL, create_engine
import os
from .models import Base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

async def get_async_session():
  """
  Asynchronously creates and returns a SQLAlchemy session object.

  Returns:
    An SQLAlchemy session object.
  """
  engine = create_async_engine(ASYNC_DATABASE_URL)
  async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  
  async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
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


def get_session():
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False)
    with Session.begin() as session:
      try:
          yield session
      except Exception as e:
        print(e)
        session.rollback()
      finally:
        session.close()
    engine.dispose()
        