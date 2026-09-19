"""
===============================================================================
Module 01: Side-by-Side Performance Comparison Benchmark
===============================================================================

CONCEPTS DEMONSTRATED:
1. Benchmarking execution speedup factor: Speedup = Sync Time / Async Time.
2. Mathematical verification of N-task latency scaling.

BENCHMARK SETUP:
- Total Tasks: 10
- Simulated Latency per Task: 0.5 seconds
- Synchronous Expected Time : 10 tasks * 0.5s = ~5.0 seconds
- Asynchronous Expected Time: max(0.5s) = ~0.5 seconds
- Expected Theoretical Speedup: ~10x
===============================================================================
"""

import asyncio
import time

NUM_TASKS = 10
SIMULATED_LATENCY = 0.5


# --- SYNCHRONOUS WORKLOAD IMPLEMENTATION ---
def sync_work(task_id: int) -> str:
    """Synchronous worker that blocks the thread for SIMULATED_LATENCY seconds."""
    time.sleep(SIMULATED_LATENCY)
    return f"Sync_Result_{task_id}"


def run_sync_benchmark() -> float:
    """Executes all 10 tasks sequentially and measures execution duration."""
    start = time.perf_counter()
    results = [sync_work(i) for i in range(1, NUM_TASKS + 1)]
    duration = time.perf_counter() - start
    print(f"[BENCHMARK] Sync completed {len(results)} tasks in {duration:.4f}s")
    return duration


# --- ASYNCHRONOUS WORKLOAD IMPLEMENTATION ---
async def async_work(task_id: int) -> str:
    """Asynchronous worker coroutine that yields control for SIMULATED_LATENCY seconds."""
    await asyncio.sleep(SIMULATED_LATENCY)
    return f"Async_Result_{task_id}"


async def run_async_benchmark() -> float:
    """Schedules all 10 tasks concurrently on the event loop and measures duration."""
    start = time.perf_counter()
    tasks = [async_work(i) for i in range(1, NUM_TASKS + 1)]
    results = await asyncio.gather(*tasks)
    duration = time.perf_counter() - start
    print(f"[BENCHMARK] Async completed {len(results)} tasks in {duration:.4f}s")
    return duration


def main():
    print("=================================================================")
    print(f"   BENCHMARKING {NUM_TASKS} I/O TASKS (Latency = {SIMULATED_LATENCY}s per task)")
    print("=================================================================")
    
    # 1. Run Synchronous Benchmark
    print("\n1. Executing Synchronous Sequential Pipeline...")
    sync_duration = run_sync_benchmark()
    
    # 2. Run Asynchronous Benchmark
    print("\n2. Executing Asynchronous Concurrent Pipeline...")
    async_duration = asyncio.run(run_async_benchmark())
    
    # 3. Calculate Speedup
    speedup = sync_duration / async_duration if async_duration > 0 else 0.0
    
    print("\n=================================================================")
    print("                      BENCHMARK RESULTS                          ")
    print("=================================================================")
    print(f" Synchronous Total Duration : {sync_duration:.4f} seconds")
    print(f" Asynchronous Total Duration: {async_duration:.4f} seconds")
    print(f" Performance Acceleration  : [SPEEDUP] {speedup:.2f}x Faster!")
    print("=================================================================")


if __name__ == "__main__":
    main()
