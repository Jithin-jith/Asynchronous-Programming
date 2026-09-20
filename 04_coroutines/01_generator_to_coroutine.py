"""
===============================================================================
Module 04: Generator-Based Coroutine Evolution & Two-Way Communication
===============================================================================

CONCEPTS DEMONSTRATED:
1. Generator Stack Frame Pausing & Resuming:
   - Generator functions preserve local variables and instruction pointers at `yield`.

2. Bidirectional Data Flow & Value Transformation:
   - Calling `gen.send(input_val)` passes `input_val` INTO the generator frame.
   - The generator modifies/transforms `input_val` (e.g. string upper-casing, math calculations).
   - The modified result is yielded BACK OUT to the caller as the return value of `.send()`.

3. Generator Return Values & Termination (PEP 380):
   - When a generator executes `return`, CPython raises `StopIteration(return_value)`.
   - The final result payload is encapsulated inside `StopIteration.value`.

HOW THIS CODE WORKS:
- `next(gen)` primes the generator (yields `"READY_FOR_INPUT"`).
- `gen.send("hello coroutine")` receives `"hello coroutine"`, transforms it to `"PROCESSED: HELLO COROUTINE"`, and yields it back to `main()`.
- `gen.send(50)` receives `50`, calculates $50 \times 2 = 100$, and yields `"CALCULATED_RESULT: 100"` back to `main()`.
- `gen.send("FINISH")` completes the generator, returning `"COROUTINE_PIPELINE_COMPLETE"`.
===============================================================================
"""


def generator_coroutine():
    """Generator-based coroutine receiving values, transforming them, and reflecting them back.

    Demonstrates bidirectional processing:
    Caller -> .send(val) -> Generator receives -> Generator transforms -> yield transformed_val -> Caller receives

    Yields:
        str: Transformed data payloads emitted back to the caller.

    Returns:
        str: Final result payload attached to StopIteration.value upon completion.
    """
    # Line 1: Log initial execution entry when generator is primed by next()
    print(" -> [GenCoro] Function execution started! Pausing at initial yield...")

    # Line 2: INITIAL YIELD (Priming Phase)
    # Yields "READY_FOR_INPUT" OUT to caller.
    # When caller invokes gen.send("hello coroutine"), execution resumes and assigns string to 'received_text'.
    received_text = yield "READY_FOR_INPUT"

    # Line 3: Transform received string value (Upper-case transformation)
    print(f" -> [GenCoro] Resumed! Received text input: '{received_text}'")
    transformed_text = f"PROCESSED: {received_text.upper()}"

    # Line 4: SECOND YIELD (Reflecting Transformed Text Back to Caller)
    # Yields 'transformed_text' BACK OUT to caller while pausing to receive a numeric input next.
    received_number = yield transformed_text

    # Line 5: Transform received numeric value (Math calculation: input * 2)
    print(f" -> [GenCoro] Resumed! Received numeric input: {received_number}")
    calculated_val = received_number * 2
    transformed_math = f"CALCULATED_RESULT: {calculated_val}"

    # Line 6: THIRD YIELD (Reflecting Calculated Result Back to Caller)
    # Yields 'transformed_math' BACK OUT to caller while pausing for finalization signal.
    _ = yield transformed_math

    # Line 7: TERMINATION & RETURN
    print(" -> [GenCoro] Received final signal. Terminating generator...")
    return "COROUTINE_PIPELINE_COMPLETE"


def main():
    """Main routine driving generator through bidirectional send/yield data transformation steps."""

    # Line 1: Print section header banner
    print("=== Generator-Based Coroutine (Bidirectional Transformation Demo) ===")

    # Line 2: Instantiate generator object (GEN_CREATED state - does not run code yet)
    gen = generator_coroutine()
    print(f"Created generator object: {gen}\n")

    # Line 3: STEP 1 - Priming the Generator with next()
    # Advances execution to the first yield point ("READY_FOR_INPUT").
    primed_status = next(gen)
    print(f"[Main] Step 1 - Generator Primed. Yielded: '{primed_status}'\n")

    # Line 4: STEP 2 - Sending String & Receiving Transformed Upper-Case Output
    # gen.send("hello coroutine") passes text IN, generator transforms it to "PROCESSED: HELLO COROUTINE",
    # and yields the transformed string BACK OUT to 'text_response'.
    input_str = "hello coroutine"
    print(f"[Main] Step 2 - Sending Input Text: '{input_str}'...")
    text_response = gen.send(input_str)
    print(f"[Main] Step 2 - Received Transformed Output: '{text_response}'\n")

    # Line 5: STEP 3 - Sending Number & Receiving Calculated Math Result
    # gen.send(50) passes number 50 IN, generator calculates 50 * 2 = 100,
    # and yields "CALCULATED_RESULT: 100" BACK OUT to 'math_response'.
    input_num = 50
    print(f"[Main] Step 3 - Sending Numeric Input: {input_num}...")
    math_response = gen.send(input_num)
    print(f"[Main] Step 3 - Received Calculated Output: '{math_response}'\n")

    # Line 6: STEP 4 - Finalizing Generator & Extracting Return Value
    try:
        print("[Main] Step 4 - Sending Finalization Signal...")
        gen.send("FINISH")
    except StopIteration as e:
        # Catch StopIteration and extract generator return value from e.value
        print(f"[Main] Step 4 - Generator completed! Final Return Value (StopIteration.value): '{e.value}'")


if __name__ == "__main__":
    # Line 1: Execute main routine when script is run directly from shell
    main()


