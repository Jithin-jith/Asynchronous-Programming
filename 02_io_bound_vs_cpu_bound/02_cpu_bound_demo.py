"""
===============================================================================
Module 02: CPU-Bound Workload Anti-Pattern Demo
===============================================================================

CONCEPTS DEMONSTRATED:
1. CPU-Bound vs. I/O-Bound Workloads:
   - I/O-bound tasks spend most time waiting for external events (disk, network, DB).
   - CPU-bound tasks spend most time actively executing math/logic instructions on the CPU core.

2. Single-Threaded Cooperative Multitasking:
   - `asyncio` runs on a SINGLE OS thread by default.
   - Concurrency requires yield points (`await`). Without yield points, the single
     thread is continuously held, preventing any other coroutine from executing.

3. The `async def` Misconception (Anti-Pattern):
   - Simply wrapping a synchronous CPU-heavy function in `async def` does NOT make it 
     asynchronous or non-blocking.
   - If a coroutine contains no `await` expressions to return control to the event loop,
     it will run synchronously to completion, hogging the thread and event loop.

4. The CPython Global Interpreter Lock (GIL):
   - CPython's GIL restricts Python bytecode execution to a single thread at a time per process.
   - Pure `asyncio` does NOT bypass the GIL, nor does it spawn multiple OS threads or processes.

5. Correct Solutions for CPU-Bound Code:
   - Use `concurrent.futures.ProcessPoolExecutor` or `asyncio.loop.run_in_executor` to offload work to separate Python processes (multi-core parallelism).
   - For light blocking I/O or C-extension calls, `asyncio.to_thread` may be used.
   - Use compiled libraries (NumPy, Cython, C/Rust extensions) that release the GIL.

HOW THIS CODE WORKS:
- `compute_heavy_math(n)` performs 15 million sum-of-squares iterations (CPU-bound).
- `async_wrapper(n)` wraps `compute_heavy_math(n)` in an `async def` function.
- We schedule 4 tasks concurrently using `asyncio.gather(*tasks)`.
- OBSERVED RESULT: The tasks execute strictly sequentially (Task 1 -> Task 2 -> Task 3 -> Task 4).
  Total Execution Time = T1 + T2 + T3 + T4 (~8-10 seconds total).
===============================================================================
"""

import asyncio
import time


def compute_heavy_math(n: int) -> int:
    """Performs a CPU-intensive sum-of-squares computation.

    This function represents a classic CPU-bound workload: prime generation, data processing,
    image manipulation, machine learning inference, or heavy mathematical calculations.

    Args:
        n (int): The number of iterations to perform.

    Returns:
        int: The resulting sum of squares.
    """
    print(f"[CPU Task] Calculating sum of squares for N = {n:,}...")

    # CPU-BOUND BOTTLENECK:
    # This loop spends 100% of its execution time actively crunching numbers on a single CPU core.
    # Because this is standard synchronous Python code, it does NOT yield control back to the event loop.
    # The GIL remains locked by this thread for the entire duration of the computation.
    total = sum(i * i for i in range(n))

    print(f"[CPU Task] Finished calculation for N = {n:,}")
    return total


async def async_wrapper(n: int) -> int:
    """Coroutine wrapper around synchronous CPU-bound math function.

    ANTI-PATTERN WARNING:
    Defining a function with 'async def' creates a coroutine, but it DOES NOT automatically 
    make synchronous blocking code asynchronous or non-blocking!

    Why this blocks:
    - For a coroutine to be cooperative, it MUST contain 'await' statements that yield 
      control back to the asyncio event loop (e.g., awaiting non-blocking I/O).
    - Calling 'compute_heavy_math(n)' directly inside an async function executes the math
      synchronously on the main event loop thread, completely blocking all other scheduled tasks.

    Args:
        n (int): Iteration count passed to compute_heavy_math.

    Returns:
        int: Computed sum.
    """
    # NO 'await' here! The event loop thread will be hijacked until compute_heavy_math completes.
    return compute_heavy_math(n)


async def main():
    print("=== Running CPU-Bound Calculations Sequentially in Async Event Loop ===")
    start_time = time.perf_counter()

    n_iterations = 15_000_000

    # STEP 1: Instantiate 4 coroutine objects for CPU calculations.
    # Note: Creating coroutines does not execute them yet; it only prepares them.
    tasks = [async_wrapper(n_iterations) for _ in range(4)]

    # STEP 2: Schedule all 4 tasks with asyncio.gather().
    # INTENT: The programmer hopes these 4 tasks will run concurrently and finish faster.
    # REALITY: asyncio.gather starts Task 1. Task 1 executes compute_heavy_math without yielding.
    #          Task 1 blocks the event loop thread for ~2+ seconds.
    #          Once Task 1 finishes, the event loop can finally move to Task 2, then Task 3, then Task 4.
    results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start_time

    # STEP 3: Print benchmark summary and architectural warnings.
    print(f"\n[SUMMARY] Completed {len(results)} CPU-bound tasks in {elapsed:.2f} seconds!")
    print("-" * 75)
    print("[WARNING] NOTICE THE ANTI-PATTERN:")
    print("  1. Even though we used 'asyncio.gather', execution was STRICTLY SEQUENTIAL.")
    print("  2. Total time equals the SUM of all 4 task durations (T1 + T2 + T3 + T4).")
    print("  3. Reason: asyncio handles single-threaded I/O concurrency, NOT CPU parallelism.")
    print("  4. Solution: For CPU-bound tasks, use Multiprocessing (ProcessPoolExecutor)")
    print("     to utilize multiple CPU cores and bypass the CPython GIL.")
    print("-" * 75)


if __name__ == "__main__":
    # Entry point: Starts the asyncio event loop and executes main()
    asyncio.run(main())

