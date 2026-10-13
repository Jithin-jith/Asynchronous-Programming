"""
===============================================================================
Module 04: Generator-Based Coroutine Evolution & Two-Way Communication
===============================================================================

CONCEPTS DEMONSTRATED:
1. Generator Stack Frame Pausing & Resuming:
   - Generator functions preserve local variables and instruction pointers at `yield`.
2. Bidirectional Data Flow & Value Transformation:
   - Calling `gen.send(input_val)` passes `input_val` INTO the generator frame.
   - The generator transforms the input (e.g. formatting customer records and crafting LLM prompts).
   - The modified payload is yielded BACK OUT to the caller as the return value of `.send()`.
3. Generator Return Values & Termination (PEP 380):
   - When a generator executes `return`, CPython raises `StopIteration(return_value)`.
   - The final result payload is encapsulated inside `StopIteration.value`.

HOW THIS CODE WORKS:
- `db_prompt_pipeline_coroutine()` acts as a bidirectional processing pipeline.
- Step 1: `next(gen)` primes the generator (yields `"READY_FOR_DATA"`).
- Step 2: `gen.send(customer_dict)` formats customer data into a prompt template and yields it back.
- Step 3: `gen.send(prompt_config)` applies temperature/model settings and yields ready payload.
- Step 4: Final signal returns completion status attached to `StopIteration.value`.
===============================================================================
"""


def db_prompt_pipeline_coroutine():
    """Generator-based coroutine receiving customer database records and generating LLM prompts.

    Demonstrates bidirectional processing:
    Caller -> .send(db_record) -> Coroutine crafts prompt -> yield prompt -> Caller receives
    """
    print(" -> [GenCoro] Pipeline initialized. Waiting at initial yield for database record...")

    # Step 1: Priming phase
    user_record = yield "READY_FOR_DATA"

    # Step 2: Transform user record into an LLM prompt string
    print(f" -> [GenCoro] Received customer record for: {user_record.get('name')}")
    crafted_prompt = (
        f"Prompt: Generate personalized product recommendations for {user_record.get('name')} "
        f"({user_record.get('role')}) with {user_record.get('order_count', 0)} past orders."
    )
    model_config = yield crafted_prompt

    # Step 3: Transform model configuration
    print(f" -> [GenCoro] Received model configuration: {model_config}")
    final_payload = {
        "model": model_config.get("model", "gemini-2.5-flash"),
        "contents": crafted_prompt,
        "temperature": model_config.get("temperature", 0.7),
        "status": "READY_TO_DISPATCH"
    }
    _ = yield final_payload

    # Step 4: Termination
    print(" -> [GenCoro] Finalizing pipeline execution...")
    return "PIPELINE_PAYLOAD_SUCCESSFULLY_BUILT"


def main():
    print("=================================================================")
    print("  MODULE 04: GENERATOR COROUTINE (BIDIRECTIONAL DATA PIPELINE)")
    print("=================================================================")

    gen = db_prompt_pipeline_coroutine()
    print(f"Created generator object: {gen}\n")

    # Step 1: Prime generator
    status = next(gen)
    print(f"[Main] Step 1 - Primed generator. Received status: '{status}'\n")

    # Step 2: Send customer database record
    sample_customer = {"name": "Diana Prince", "role": "premium", "order_count": 3}
    print(f"[Main] Step 2 - Sending SQLite customer record: {sample_customer}...")
    crafted_prompt = gen.send(sample_customer)
    print(f"[Main] Step 2 - Received crafted prompt:\n  '{crafted_prompt}'\n")

    # Step 3: Send LLM model configuration
    config = {"model": "gemini-2.5-flash", "temperature": 0.2}
    print(f"[Main] Step 3 - Sending model configuration: {config}...")
    ready_payload = gen.send(config)
    print(f"[Main] Step 3 - Received ready LLM dispatch payload:\n  {ready_payload}\n")

    # Step 4: Finalize generator
    try:
        print("[Main] Step 4 - Finalizing generator...")
        gen.send("COMPLETE")
    except StopIteration as e:
        print(f"[Main] Step 4 - Pipeline finished! Return value: '{e.value}'")

    print("=================================================================\n")


if __name__ == "__main__":
    main()
