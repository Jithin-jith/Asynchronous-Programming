"""
===============================================================================
Module 09: Exception Groups & Subgroup Filtering (`except*`)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Handling concurrent exceptions in Python 3.11+.
2. Filtering exception types using `except* ExceptionType` syntax.
3. Real-world exceptions:
   - Worker 1: Real SQLite `aiosqlite.OperationalError` (syntax error / invalid table).
   - Worker 2: Prompt validation `ValueError` (invalid temperature parameter).
4. Graceful aggregation inside `ExceptionGroup`.

HOW THIS CODE WORKS:
- Two background tasks raise different exceptions concurrently in a `TaskGroup`.
- `TaskGroup` packages them inside an `ExceptionGroup`.
- `except* aiosqlite.OperationalError` catches only database errors.
- `except* ValueError` catches only parameter validation errors.
===============================================================================
"""

import sys
import asyncio
import aiosqlite
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"


async def worker_database_query_error():
    """Worker that triggers an SQLite OperationalError."""
    print("  [Worker 1 - DB] Running malformed query on SQLite...")
    await asyncio.sleep(0.05)
    async with aiosqlite.connect(DB_PATH) as db:
        # Intentionally invalid SQL syntax
        await db.execute("SELEC * FORM invalid_syntax_table")


async def worker_llm_parameter_error():
    """Worker that triggers a ValueError due to invalid LLM settings."""
    print("  [Worker 2 - LLM] Validating LLM hyper-parameters...")
    await asyncio.sleep(0.05)
    temperature = 2.5
    if temperature > 2.0:
        raise ValueError(f"Gemini temperature {temperature} exceeds allowable range (0.0 - 2.0)!")


async def main():
    print("=================================================================")
    print("  MODULE 09: EXCEPTIONGROUP FILTERING WITH except* (REAL I/O)")
    print("=================================================================")

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(worker_database_query_error(), name="DB_Error_Task")
            tg.create_task(worker_llm_parameter_error(), name="LLM_Error_Task")
    except* aiosqlite.OperationalError as db_errors:
        print(f"\n[OK] Handled SQLite Errors cleanly ({len(db_errors.exceptions)} error):")
        for err in db_errors.exceptions:
            print(f"  -> SQLite Error: {err}")
    except* ValueError as val_errors:
        print(f"\n[OK] Handled Validation Errors cleanly ({len(val_errors.exceptions)} error):")
        for err in val_errors.exceptions:
            print(f"  -> Validation Error: {err}")

    print("\nTakeaway: except* allows independent, clean handling for each error domain!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
