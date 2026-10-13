"""
===============================================================================
Module 13: Preventing Race Conditions with asyncio.Lock (SQLite Inventory)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Race conditions across `await` yield points in single-threaded asyncio.
2. Protecting shared state using `async with lock:`.
3. Real-world scenario: Multiple concurrent customers trying to purchase the last
   remaining inventory units of a product.
4. Serializing read-modify-write critical sections without OS thread locks.

HOW THIS CODE WORKS:
- Initial stock = 10 units. 15 concurrent customers attempt to buy 1 unit each.
- Unlocked Mode: Interleaved yields across `await` cause over-selling (negative stock or lost updates).
- Locked Mode: `async with inventory_lock:` guarantees atomic stock verification and decrement.
===============================================================================
"""

import asyncio

# Shared stock counter
inventory_stock = 10
stock_lock = asyncio.Lock()


async def purchase_item(customer_id: int, use_lock: bool) -> bool:
    """Attempts to purchase 1 unit from shared inventory."""
    global inventory_stock

    if use_lock:
        async with stock_lock:
            # Critical Section: Check Stock -> Await Async Step -> Decrement
            current_stock = inventory_stock
            await asyncio.sleep(0.001)  # Context switch point
            if current_stock > 0:
                inventory_stock = current_stock - 1
                return True
            return False
    else:
        # WITHOUT LOCK: Race condition across await point!
        current_stock = inventory_stock
        await asyncio.sleep(0.001)
        if current_stock > 0:
            inventory_stock = current_stock - 1
            return True
        return False


async def run_purchase_simulation(use_lock: bool) -> tuple[int, int]:
    """Simulates 15 concurrent purchases on 10 stock items."""
    global inventory_stock
    inventory_stock = 10

    tasks = [purchase_item(i, use_lock) for i in range(1, 16)]
    results = await asyncio.gather(*tasks)
    successful_purchases = sum(1 for r in results if r)
    return successful_purchases, inventory_stock


async def main():
    print("=================================================================")
    print("  MODULE 13: PREVENTING RACE CONDITIONS WITH asyncio.Lock")
    print("=================================================================")
    print("Initial Inventory: 10 units | Concurrent Purchase Requests: 15\n")

    # 1. Unlocked simulation (Demonstrates race condition & overselling)
    unlocked_bought, unlocked_left = await run_purchase_simulation(use_lock=False)
    print(f"[UNLOCKED] Purchases Approved: {unlocked_bought}/15 | Remaining Stock: {unlocked_left}")
    print("  -> Notice: Without lock, multiple coroutines read the same stock level before writing!")

    # 2. Locked simulation (Guarantees safe atomic state mutation)
    locked_bought, locked_left = await run_purchase_simulation(use_lock=True)
    print(f"\n[LOCKED]   Purchases Approved: {locked_bought}/15 | Remaining Stock: {locked_left}")
    print("  -> Notice: With asyncio.Lock, exactly 10 units sold and stock reached 0 safely!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
