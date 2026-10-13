"""
===============================================================================
Module 12: Async SQLAlchemy 2.0 Engine & Schema Setup
===============================================================================

CONCEPTS DEMONSTRATED:
1. `create_async_engine("sqlite+aiosqlite:///:memory:")`.
2. DeclarativeBase ORM mapping with Mapped and mapped_column.
3. Asynchronous schema creation via `conn.run_sync(Base.metadata.create_all)`.

HOW THIS CODE WORKS:
- `create_async_engine` initializes non-blocking `aiosqlite` connection pool.
- `conn.run_sync` executes synchronous DDL table creation within async connection.
===============================================================================
"""

import asyncio
from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""
    pass


class User(Base):
    """User ORM database table model."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)


async def init_models():
    print("=== Initializing Async SQLAlchemy 2.0 Engine & Schema ===")
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Run sync schema creation in async engine execution context
    async with engine.begin() as conn:
        print("Creating table schema in database...")
        await conn.run_sync(Base.metadata.create_all)
        print("Table 'users' created successfully!")
        
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_models())
