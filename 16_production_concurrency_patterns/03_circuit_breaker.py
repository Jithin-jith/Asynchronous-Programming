"""
===============================================================================
Module 16: Async Circuit Breaker Pattern (LLM & Remote Service Protection)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Circuit Breaker State Machine (`CLOSED`, `OPEN`, `HALF-OPEN`).
2. Fast-failing requests during downstream outages without burning resources.
3. Automated recovery probing.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- CLOSED: Calls pass through. Failures increment `failure_count`.
- Threshold reached -> State changes to OPEN. Fast-fails immediately.
- Cooldown expires -> State changes to HALF-OPEN. Probes trial request.
- Trial succeeds -> Resets state to CLOSED.
===============================================================================
"""

import time
import asyncio


class CircuitBreakerOpenException(Exception):
    """Raised when a request is rejected because the Circuit Breaker is OPEN."""
    pass


class AsyncCircuitBreaker:
    """Production Async Circuit Breaker state machine."""

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 1.5):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # States: CLOSED, OPEN, HALF-OPEN
        self.last_state_change = time.time()

    async def call(self, func, *args, **kwargs):
        """Wraps async function invocation with circuit breaker monitoring."""
        now = time.time()

        # Check if recovery timeout has passed to switch from OPEN to HALF-OPEN
        if self.state == "OPEN":
            if now - self.last_state_change > self.recovery_timeout:
                print("\n  [HALF-OPEN] Cooldown expired. Transitioning to HALF-OPEN for probe...")
                self.state = "HALF-OPEN"
            else:
                print("  [OPEN] Circuit is OPEN! Fast-failing without calling downstream.")
                raise CircuitBreakerOpenException("Circuit Breaker is OPEN. Call rejected.")

        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF-OPEN":
                print("  [CLOSED] Probe request succeeded! Resetting Circuit to CLOSED.")
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            print(f"  [CircuitBreaker] Failure detected ({self.failure_count}/{self.failure_threshold}): {e}")

            if self.failure_count >= self.failure_threshold:
                if self.state != "OPEN":
                    print(f"  [OPEN] Threshold exceeded! Tripping Circuit Breaker to OPEN for {self.recovery_timeout}s.")
                    self.state = "OPEN"
                    self.last_state_change = time.time()
            raise


# Downstream service simulation with controllable outage state
service_is_healthy = False


async def simulated_downstream_service(request_id: int) -> str:
    """Simulates an external API service that is currently experiencing an outage."""
    await asyncio.sleep(0.05)
    if not service_is_healthy:
        raise ConnectionError("503 Service Unavailable: Downstream outage")
    return f"Response for Req #{request_id}"


async def main():
    global service_is_healthy
    print("=================================================================")
    print("  MODULE 16: ASYNC CIRCUIT BREAKER PATTERN (SERVICE OUTAGE)")
    print("=================================================================")

    breaker = AsyncCircuitBreaker(failure_threshold=3, recovery_timeout=1.0)

    # 1. Trigger failures until Circuit Breaker opens
    print("Phase 1: Sending requests while downstream service is down...")
    for i in range(1, 5):
        try:
            await breaker.call(simulated_downstream_service, i)
        except Exception as exc:
            print(f"  -> Request #{i} Result: {type(exc).__name__}\n")

    # 2. Fast-failing while OPEN
    print("Phase 2: Sending request immediately while circuit is OPEN (Fast Fail)...")
    try:
        await breaker.call(simulated_downstream_service, 5)
    except CircuitBreakerOpenException:
        print("  -> Confirmed: Fast-failed instantly without network latency!\n")

    # 3. Wait for recovery cooldown and restore service
    print("Phase 3: Waiting 1.1s for recovery cooldown and restoring service...")
    await asyncio.sleep(1.1)
    service_is_healthy = True

    # 4. Probe in HALF-OPEN state to restore
    print("\nPhase 4: Sending probe request in HALF-OPEN state...")
    result = await breaker.call(simulated_downstream_service, 6)
    print(f"  -> Probe Succeeded! Result: '{result}'")
    print(f"  -> Current Circuit Breaker State: {breaker.state}")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
