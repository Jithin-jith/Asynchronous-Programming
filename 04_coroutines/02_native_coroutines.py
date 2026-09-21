"""
===============================================================================
Module 04: Native Coroutines with `async def`
===============================================================================

CONCEPTS DEMONSTRATED:
1. Defining native coroutines via `async def`.
2. Lazy evaluation: Calling coroutine function returns a coroutine object.
3. Executing coroutine objects via `asyncio.run()`.

HOW THIS CODE WORKS:
- `greet("Alice")` does NOT execute code immediately.
- It returns `<coroutine object greet at 0x...>` in a dormant state.
- Passing `coro_obj` to `asyncio.run(coro_obj)` binds it to an event loop and executes it.
===============================================================================
"""

import asyncio
import inspect


async def greet(name: str) -> str:
    """Native coroutine function defined with async def syntax."""
    print(f"Inside greet(): Hello, {name}!")
    await asyncio.sleep(5.0)
    return f"Greeting to {name} complete."


def main():
    print("=== Native Coroutine Invocation & Lazy Evaluation ===")
    
    # Invoking an async def function does NOT execute its body code!
    coro_obj = greet("Alice")
    
    print(f"Type of returned object : {type(coro_obj)}")
    print(f"Is it a coroutine object?: {asyncio.iscoroutine(coro_obj)}")
    print(f"Inspect iscoroutine()    : {inspect.iscoroutine(coro_obj)}")
    print("Notice: 'Inside greet()' has NOT been printed yet!\n")
    
    print("Now executing coroutine object with asyncio.run()...")
    result = asyncio.run(coro_obj)
    print(f"Execution output: '{result}'")


if __name__ == "__main__":
    main()
