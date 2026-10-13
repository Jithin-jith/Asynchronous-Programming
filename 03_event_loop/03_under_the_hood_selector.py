"""
===============================================================================
Module 03: Event Loop OS Selector Multiplexer Inspection
===============================================================================

CONCEPTS DEMONSTRATED:
1. Event Loop Policy (`asyncio.get_event_loop_policy()`):
   - Manages creating, retrieving, and setting the default event loop implementation for the OS platform.

2. OS-Level I/O Multiplexer Selection:
   - Linux: `_UnixSelectorEventLoop` backed by `epoll`.
   - macOS / BSD: `_UnixSelectorEventLoop` backed by `kqueue`.
   - Windows: Default `ProactorEventLoop` backed by `IocpProactor` (IO Completion Ports)
     or fallback `_WindowsSelectorEventLoop` backed by `select`.

3. Real-World Relevance:
   - This underlying OS kernel multiplexer monitors incoming network packets from
     Google Gemini LLM HTTP connections and disk file descriptors for SQLite.
   - When Gemini finishes streaming tokens or SQLite finishes writing data, the OS
     kernel signals the multiplexer, waking the coroutine immediately without polling.

HOW THIS CODE WORKS:
- Retrieves current OS platform name using `sys.platform`.
- Queries active loop policy name.
- Creates an event loop instance (`asyncio.new_event_loop()`) to inspect internal `_selector` attribute.
===============================================================================
"""

import asyncio
import sys


def inspect_selector_backend():
    """Inspects the OS-level multiplexer powering the current event loop implementation."""
    policy = asyncio.get_event_loop_policy()

    print(f"Operating System Platform: {sys.platform}")
    print(f"Active Event Loop Policy : {type(policy).__name__}")

    loop = asyncio.new_event_loop()
    try:
        loop_type = type(loop).__name__
        print(f"Event Loop Class         : {loop_type}")

        if hasattr(loop, "_selector"):
            selector_type = type(loop._selector).__name__
            print(f"OS Multiplexer Backend   : {selector_type}")
        else:
            print("OS Multiplexer Backend   : Windows Proactor (IOCP - I/O Completion Ports)")

        print("\nReal-World Role:")
        print("  This kernel multiplexer monitors network sockets for Google Gemini LLM API calls")
        print("  and disk file descriptors for SQLite without freezing the single Python thread.")
    finally:
        loop.close()


if __name__ == "__main__":
    print("=================================================================")
    print("  MODULE 03: EVENT LOOP OS MULTIPLEXER INSPECTION")
    print("=================================================================")
    inspect_selector_backend()
    print("=================================================================\n")
