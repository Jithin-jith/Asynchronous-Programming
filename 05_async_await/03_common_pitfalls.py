"""
===============================================================================
Module 05: Common Async/Await Pitfalls & Anti-Patterns
===============================================================================

CONCEPTS DEMONSTRATED:
1. Unawaited Coroutine Warning: Invoking an `async def` function without `await` 
   returns an unstarted coroutine object that will never execute its body.
2. Awaiting Non-Awaitable Objects: Attempting to `await` primitives (e.g., `int`, `str`, `dict`) 
   raises a `TypeError: object ... can't be used in 'await' expression`.
3. Blocking the Event Loop: Calling synchronous blocking functions (e.g. `time.sleep()`) 
   inside a coroutine freezes the entire event loop single thread, stalling all other concurrent tasks.

HOW THIS CODE WORKS:
- Pitfall 1: Calls `unawaited_demo()` without `await`, demonstrating that code inside the function 
  does not execute and inspecting the variable type (`<class 'coroutine'>`).
- Pitfall 2: Dynamically evaluates `await 42` to catch and display the resulting `TypeError`.
- Pitfall 3: Explains why synchronous I/O or long CPU operations block the loop thread and how 
  to prevent it (using `asyncio.to_thread` or non-blocking async primitives).
===============================================================================
"""

import asyncio


async def unawaited_demo() -> str:
    """
    A sample coroutine that returns a result. If not awaited, its body code is never executed!
    """
    print("  [Coro Body] This print statement ONLY runs if the coroutine is awaited!")
    return "Hidden Result"


async def main():
    print("=== Common Async/Await Pitfalls & Anti-Patterns Demo ===")
    
    # -------------------------------------------------------------------------
    # PITFALL 1: FORGETTING TO AWAIT A COROUTINE FUNCTION
    # - Calling `unawaited_demo()` creates the coroutine object, but does NOT run it.
    # - Notice that "[Coro Body]..." is NOT printed above!
    # -------------------------------------------------------------------------
    print("\n1. Calling unawaited_demo() WITHOUT 'await':")
    coro_ref = unawaited_demo()
    print(f"   Stored variable type: {type(coro_ref)}")
    print(f"   Value of coro_ref  : {coro_ref}")
    
    # Close explicitly to clean up frame and suppress `RuntimeWarning: coroutine was never awaited`
    coro_ref.close()
    
    # Correct usage:
    print("   [Fix] Now calling WITH 'await':")
    valid_result = await unawaited_demo()
    print(f"   Result when awaited: '{valid_result}'")
    
    # -------------------------------------------------------------------------
    # PITFALL 2: ATTEMPTING TO AWAIT A NON-AWAITABLE OBJECT
    # - Primitive types (int, float, list, dict) do not implement `__await__()`.
    # - Attempting `await 42` raises `TypeError`.
    # -------------------------------------------------------------------------
    print("\n2. Attempting to await a non-awaitable integer primitive (await 2.0):")
    
    async def _invalid_await():
        return await 2.0  # Primitive float primitive 2.0 cannot be awaited

        
    try:
        await _invalid_await()
    except TypeError as e:
        print(f"   [ERROR] Caught Expected TypeError: {e}")
        print("   [Fix] Only await Coroutines, Tasks, Futures, or objects with __await__().")


    # -------------------------------------------------------------------------
    # PITFALL 3: BLOCKING THE EVENT LOOP WITH SYNCHRONOUS CALLS
    # - Calling standard synchronous time.sleep() or blocking network calls stops 
    #   the event loop single-thread from processing ANY other concurrent tasks.
    # -------------------------------------------------------------------------
    print("\n3. Blocking the Event Loop (Conceptual Anti-Pattern):")
    print("   [Rule] Never call time.sleep(N) inside async code! Use `await asyncio.sleep(N)` instead.")
    print("   [Rule] For CPU-bound or blocking synchronous I/O, use `await asyncio.to_thread(func)`.")


if __name__ == "__main__":
    asyncio.run(main())

