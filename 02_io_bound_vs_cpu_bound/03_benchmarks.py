"""
===============================================================================
Module 02: Benchmarking CPU-Bound Tasks (Pure Asyncio vs ProcessPoolExecutor)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Pure Asyncio CPU Blocking (Main Thread Bottleneck):
   - Running heavy CPU calculations directly on the main asyncio thread freezes 
     the event loop, forcing strictly sequential execution ($T_{\\text{total}} = T_1 + T_2 + T_3 + T_4$).

2. Multiprocessing Offloading via `ProcessPoolExecutor`:
   - Spawns separate worker Python processes (one per available CPU core).
   - Each worker process gets its own independent Python interpreter and GIL instance.
   - This bypasses CPython's GIL limitation and achieves true hardware multi-core parallelism.

3. Async Integration via `loop.run_in_executor()`:
   - Converts synchronous/blocking function calls executed in worker pools into 
     awaitable `asyncio.Future` objects.
   - Allows the main event loop thread to non-blockingly `await` process execution completion.

4. Performance Speedup Ratio:
   - $\\text{Speedup} = \\frac{\\text{Time}_{\\text{Pure Asyncio}}}{\\text{Time}_{\\text{ProcessPoolExecutor}}}$
   - On a 4+ core CPU, expected speedup approaches 3x - 4x faster execution!
===============================================================================
"""

import asyncio                             # Async event loop and Future scheduling framework
from concurrent.futures import ProcessPoolExecutor  # Process pool manager for multi-core parallelism
import time                                # High-precision performance timing library


def cpu_work(n: int) -> int:
    """Synchronous CPU-bound sum-of-squares calculation.

    This function represents a pure CPU-intensive task (e.g., matrix computation,
    image processing, cryptography, or heavy data transformation).

    Args:
        n (int): Number of loop iterations.

    Returns:
        int: The resulting sum of squares.
    """
    # Line 1: Execute 100% CPU-bound loop calculation over 'n' iterations
    # Note: This operation pins a single CPU core and locks the GIL while running in standard Python.
    return sum(i * i for i in range(n))


async def run_pure_asyncio(counts: list[int]) -> float:
    """Executes multiple CPU-bound tasks sequentially on the main asyncio event loop thread.

    ANTI-PATTERN DEMO:
    Even though this is an 'async def' function, it invokes 'cpu_work' directly without yielding.
    As a result, all 4 calculations run sequentially on the single main thread.

    Args:
        counts (list[int]): List of iteration counts for each task.

    Returns:
        float: Total execution time in seconds.
    """
    # Line 1: Capture start timestamp before starting calculations
    start = time.perf_counter()
    
    # Line 2: Execute all CPU calculations sequentially using a list comprehension on the main thread
    # The event loop thread is held continuously for each item in 'counts' without yielding.
    results = [cpu_work(c) for c in counts]
    
    # Line 3: Calculate and return total elapsed execution time
    return time.perf_counter() - start


async def run_multiprocessing(counts: list[int]) -> float:
    """Executes CPU-bound tasks in true parallel across multiple OS child processes.

    PROPER SOLUTION:
    Uses ProcessPoolExecutor to distribute tasks across CPU cores. Bridges process execution
    with asyncio using loop.run_in_executor().

    Args:
        counts (list[int]): List of iteration counts for each task.

    Returns:
        float: Total execution time in seconds.
    """
    # Line 1: Capture start timestamp before launching process pool
    start = time.perf_counter()
    
    # Line 2: Obtain reference to the currently running asyncio event loop
    loop = asyncio.get_running_loop()
    
    # Line 3: Initialize ProcessPoolExecutor context manager
    # By default, ProcessPoolExecutor creates worker processes equal to os.cpu_count().
    # Each child process runs independently with its own memory space and GIL instance!
    with ProcessPoolExecutor() as pool:
        
        # Line 4: Schedule each CPU task in the ProcessPoolExecutor using loop.run_in_executor()
        # 'loop.run_in_executor(pool, cpu_work, c)' submits 'cpu_work(c)' to an idle worker process
        # and returns an asyncio.Future object that main thread can await without blocking.
        futures = [loop.run_in_executor(pool, cpu_work, c) for c in counts]
        
        # Line 5: Await all process pool futures concurrently with asyncio.gather()
        # While child processes execute calculations on CPU cores 1, 2, 3, 4 in parallel,
        # the main asyncio thread safely waits for IPC (Inter-Process Communication) completion signals.
        results = await asyncio.gather(*futures)
        
    # Line 6: Calculate and return total elapsed execution time
    return time.perf_counter() - start


def main():
    """Main benchmark suite entry point comparing Pure Asyncio vs ProcessPoolExecutor."""
    
    # Line 1: Define test parameters (4 identical heavy tasks with N = 12,000,000)
    counts = [12_000_000] * 4
    
    # Line 2: Print visual benchmark banner to standard output
    print("=================================================================")
    print("   CPU-BOUND BENCHMARK: PURE ASYNCIO vs PROCESS POOL EXECUTOR    ")
    print("=================================================================")
    
    # Line 3: Output Phase 1 description
    print("\n1. Running Pure Asyncio (Main Thread Sequential)...")
    
    # Line 4: Run Pure Asyncio test using asyncio.run() to launch event loop
    pure_time = asyncio.run(run_pure_asyncio(counts))
    
    # Line 5: Print Pure Asyncio execution duration metric
    print(f"   Pure Asyncio Duration : {pure_time:.4f} seconds")
    
    # Line 6: Output Phase 2 description
    print("\n2. Running ProcessPoolExecutor (Multi-Core Parallel)...")
    
    # Line 7: Run Multiprocessing test using asyncio.run() to launch event loop
    mp_time = asyncio.run(run_multiprocessing(counts))
    
    # Line 8: Print ProcessPoolExecutor execution duration metric
    print(f"   ProcessPool Duration  : {mp_time:.4f} seconds")
    
    # Line 9: Calculate parallel speedup acceleration multiplier ratio
    speedup = pure_time / mp_time if mp_time > 0 else 0.0
    
    # Line 10: Output final benchmark summary and performance acceleration multiplier
    print("\n=================================================================")
    print(f" [SPEEDUP] Multiprocessing Acceleration: {speedup:.2f}x Faster!")
    print("=================================================================")


if __name__ == "__main__":
    # Line 1: Execute main benchmark routine when script is run directly from shell
    main()

