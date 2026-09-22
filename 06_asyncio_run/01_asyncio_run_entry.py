"""
===============================================================================
Module 06: Standard asyncio.run() Application Entry Point
===============================================================================

CONCEPTS DEMONSTRATED:
1. Standard application main entry point via `asyncio.run()`.
2. Automatic loop setup, main task execution, and teardown.

HOW THIS CODE WORKS:
- `if __name__ == "__main__":` invokes `asyncio.run(async_main())`.
- `asyncio.run()` creates a fresh loop, runs `async_main()`, closes background tasks,
  and shuts down the loop instance cleanly upon return.
===============================================================================
"""

import asyncio


async def async_main() -> str:
    """Root main coroutine representing application lifecycle."""
    print("[Main Coroutine] Application initialized.")
    await asyncio.sleep(5.0)
    print("[Main Coroutine] Work completed successfully.")
    return "SUCCESS_CODE_0"


if __name__ == "__main__":
    print("=== Launching Application via asyncio.run() ===")
    exit_status = asyncio.run(async_main())
    print(f"Application returned exit status: '{exit_status}'")
