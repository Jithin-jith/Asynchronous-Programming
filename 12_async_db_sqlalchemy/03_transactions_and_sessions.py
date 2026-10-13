"""
===============================================================================
Module 12: Transaction Boundaries & Automatic Rollbacks
===============================================================================

CONCEPTS DEMONSTRATED:
1. Transaction scope isolation with `async with session.begin():`.
2. Automatic transaction rollback on uncaught exceptions.

HOW THIS CODE WORKS:
- Seed account balance = $500.0.
- Inside transaction block: Deduct $100 (balance = $400), then raise RuntimeError.
- Exception triggers automatic ROLLBACK.
- Re-querying account balance confirms balance remains $500.0 (unmodified).
===============================================================================
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class Base(DeclarativeBase):
    pass


class BankAccount(Base):
    __tablename__ = "accounts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(nullable=False)
    balance: Mapped[float] = mapped_column(nullable=False)


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Seed account
    async with async_session() as session:
        async with session.begin():
            session.add(BankAccount(owner="Alice", balance=500.0))
            
    print("=== Testing Automatic Transaction Rollback ===")
    try:
        async with async_session() as session:
            async with session.begin():
                # Deduct 100
                account = (await session.execute(select(BankAccount).where(BankAccount.owner == "Alice"))).scalar_one()
                account.balance -= 100.0
                print(f"Subtracted 100, temporary balance: ${account.balance}")
                
                # Simulate mid-transaction crash!
                raise RuntimeError("Network crash before final transfer completion!")
    except RuntimeError as e:
        print(f"[ERROR] Exception caught: {e}")
        
    # Verify database state rolled back balance to 500.0
    async with async_session() as session:
        account = (await session.execute(select(BankAccount).where(BankAccount.owner == "Alice"))).scalar_one()
        print(f"\n[OK] Balance after rollback: ${account.balance:.2f} (Rollback preserved original balance!)")
        
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
