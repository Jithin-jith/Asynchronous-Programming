"""
===============================================================================
Module 12: Async CRUD Operations with SQLAlchemy 2.0
===============================================================================

CONCEPTS DEMONSTRATED:
1. `async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)`.
2. Async Create, Read, Update, Delete queries using `select()`, `update()`, `delete()`.

HOW THIS CODE WORKS:
- Create: `session.add_all([p1, p2])` inside `async with session.begin():`.
- Read: `await session.execute(select(Product))` returns scalar ORM instances.
- Update: `await session.execute(update(Product)...)`.
- Delete: `await session.execute(delete(Product)...)`.
===============================================================================
"""

import asyncio
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("=== 1. CREATE: Inserting Async ORM Records ===")
    async with async_session() as session:
        async with session.begin():
            p1 = Product(name="Laptop", price=999.99)
            p2 = Product(name="Keyboard", price=49.99)
            session.add_all([p1, p2])
            
    print("=== 2. READ: Querying Records Asynchronously ===")
    async with async_session() as session:
        stmt = select(Product).where(Product.price > 10.0)
        result = await session.execute(stmt)
        products = result.scalars().all()
        for p in products:
            print(f" -> Found Product #{p.id}: {p.name} (${p.price})")
            
    print("=== 3. UPDATE: Modifying Price ===")
    async with async_session() as session:
        async with session.begin():
            stmt = update(Product).where(Product.name == "Keyboard").values(price=59.99)
            await session.execute(stmt)
            
    print("=== 4. DELETE: Removing Record ===")
    async with async_session() as session:
        async with session.begin():
            stmt = delete(Product).where(Product.name == "Laptop")
            await session.execute(stmt)
            
    await engine.dispose()
    print("Async DB CRUD Operations Completed Successfully!")


if __name__ == "__main__":
    asyncio.run(main())
