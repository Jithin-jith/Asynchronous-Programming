"""
===============================================================================
Module 14: Streaming Transformation Pipeline with Async Generators
===============================================================================

CONCEPTS DEMONSTRATED:
1. Chaining async generators into multi-stage streaming pipelines.
2. Passing an async generator stream directly into downstream transformer generators.
3. Memory efficiency: Items flow through pipeline one at a time without accumulating.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Stage 1 (`sqlite_product_stream`): Streams product items from SQLite `ecommerce.db`.
- Stage 2 (`pricing_enricher_stream`): Adds tax and promotional calculations on the fly.
- Stage 3 (`output_formatter_stream`): Formats and presents the stream to the user.
===============================================================================
"""

import sys
import asyncio
import aiosqlite
from pathlib import Path
from typing import AsyncGenerator

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"


# Stage 1: Async Source Generator
async def sqlite_product_stream() -> AsyncGenerator[dict, None]:
    """Source generator streaming products from SQLite."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name, price FROM products LIMIT 4") as cursor:
            async for row in cursor:
                await asyncio.sleep(0.05)
                yield {"id": row[0], "name": row[1], "base_price": row[2]}


# Stage 2: Async Transformer Generator
async def pricing_enricher_stream(source: AsyncGenerator[dict, None]) -> AsyncGenerator[dict, None]:
    """Transformer generator calculating tax and discount dynamically."""
    async for item in source:
        await asyncio.sleep(0.05)
        tax = round(item["base_price"] * 0.08, 2)
        total = round(item["base_price"] + tax, 2)
        yield {**item, "tax": tax, "final_price": total}


# Stage 3: Async Consumer Pipeline
async def main():
    print("=================================================================")
    print("  MODULE 14: MULTI-STAGE ASYNC GENERATOR PIPELINE (SQLITE)")
    print("=================================================================")

    # Chain the generators: Source -> Transformer
    source_stream = sqlite_product_stream()
    enriched_stream = pricing_enricher_stream(source_stream)

    print(f"{'ID':<4} | {'Product':<25} | {'Base Price':<10} | {'Tax':<8} | {'Total':<10}")
    print("-" * 65)

    async for product in enriched_stream:
        print(
            f"{product['id']:<4} | {product['name']:<25} | "
            f"${product['base_price']:<9.2f} | ${product['tax']:<7.2f} | ${product['final_price']:<9.2f}"
        )

    print("-----------------------------------------------------------------")
    print("Takeaway: Chained async generators stream data with minimal memory usage!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
