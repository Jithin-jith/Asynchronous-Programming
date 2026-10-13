# Module 10: Async HTTP Requests & Google Gemini LLM Calls

## 📌 Executive Summary
LLM generation API calls are **I/O-bound network requests**. When building modern AI applications (agents, RAG pipelines, batch prompt processing), synchronous HTTP calls create severe latency bottlenecks. This module demonstrates non-blocking network I/O using `httpx.AsyncClient` and asynchronous Google Gemini LLM generation via `google-genai` (`client.aio`) with automatic persistence into **SQLite** (`ecommerce.db`).

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_async_httpx_basics.py` | Connection pooling with `httpx.AsyncClient` | Demonstrates non-blocking HTTP GET requests and TCP connection reuse. |
| `02_gemini_async_llm.py` | Asynchronous Google Gemini call + SQLite persistence | Invokes `client.aio.models.generate_content` and saves generation logs into SQLite `ai_logs`. |
| `03_batch_llm_prompts.py` | Concurrent Gemini prompt batching with `asyncio.gather` | Parallelizes 3 LLM prompts, reducing total duration from ~10s sequentially to ~3s concurrently. |

---

## 🏃 Expected Console Outputs

### Running `02_gemini_async_llm.py`:
```text
=================================================================
  MODULE 10: ASYNC GOOGLE GEMINI API CALL + SQLITE LOGGING
=================================================================
[Gemini] Connecting to Gemini API via client.aio...
--- Gemini Response ---
Asynchronous I/O prevents server threads from stalling during LLM generation.
-----------------------

  [DB Logger] Saving interaction to ecommerce.db ai_logs table...
  [DB Logger] Successfully logged LLM generation record!
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: Why does batching 10 Gemini prompts with `asyncio.gather()` take almost the same time as sending 1 prompt?
   - *Answer*: Because LLM calls are network I/O-bound. While the first prompt waits for model inference and network packets, the event loop dispatches the remaining 9 prompts concurrently over independent HTTP/2 or multiplexed sockets.
