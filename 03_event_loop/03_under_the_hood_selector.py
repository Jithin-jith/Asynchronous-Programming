"""
===============================================================================
Module 03: Event Loop OS Selector Multiplexer Inspection
===============================================================================

CONCEPTS DEMONSTRATED:
1. Event Loop Policy (`asyncio.get_event_loop_policy()`):
   - Manages creating, retrieving, and setting the default event loop implementation for the OS platform.

2. OS-Level I/O Multiplexer Selection:
   - Linux: `_UnixSelectorEventLoop` backed by `epoll` (`epollserver`).
   - macOS / BSD: `_UnixSelectorEventLoop` backed by `kqueue`.
   - Windows: Default `ProactorEventLoop` backed by `IocpProactor` (IO Completion Ports)
     or fallback `_WindowsSelectorEventLoop` backed by `select`.

HOW THIS CODE WORKS:
- Retrieves current OS platform name using `sys.platform`.
- Queries active loop policy name.
- Creates a temporary loop instance (`asyncio.new_event_loop()`) to inspect internal `_selector` attribute.
===============================================================================
"""

import asyncio  # Standard library async I/O framework
import sys      # System-specific parameters and functions (used to inspect OS platform)


def inspect_selector_backend():
    """Inspects the OS-level multiplexer powering the current event loop implementation."""
    
    # Line 1: Get global default event loop policy instance
    policy = asyncio.get_event_loop_policy()
    
    # Line 2: Output operating system platform string ('win32', 'linux', 'darwin')
    print(f"Operating System Platform: {sys.platform}")
    
    # Line 3: Print name of active event loop policy class
    print(f"Active Event Loop Policy : {type(policy).__name__}")
    
    # Line 4: Create a new unstarted event loop instance to inspect internal attributes
    loop = asyncio.new_event_loop()
    
    try:
        # Line 5: Query class name of instantiated event loop
        loop_type = type(loop).__name__
        print(f"Event Loop Class         : {loop_type}")
        
        # Line 6: Check if loop relies on a Selector backend (epoll / kqueue / select)
        if hasattr(loop, "_selector"):
            # Line 7: Read class name of internal selector backend object
            selector_type = type(loop._selector).__name__
            print(f"OS Multiplexer Backend   : {selector_type}")
        else:
            # Line 8: If no _selector attribute exists, Windows Proactor IOCP engine is active
            print("OS Multiplexer Backend   : Windows Proactor (IOCP - I/O Completion Ports)")
            
    finally:
        # Line 9: Explicitly close temporary event loop instance to free OS resources
        loop.close()


if __name__ == "__main__":
    # Line 1: Output section header banner
    print("=== Event Loop OS Multiplexer Inspection ===")
    
    # Line 2: Run inspection function directly
    inspect_selector_backend()

