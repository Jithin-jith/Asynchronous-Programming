# Module 12: Async Databases & SQLAlchemy 2.0 ORM

## 📌 Executive Summary
Standard relational database drivers (like `sqlite3` or `psycopg2`) are synchronous and block the Python main thread during query execution. In asynchronous web applications (FastAPI), executing synchronous database queries stalls the event loop. This module covers SQLAlchemy 2.0 async ORM architecture using non-blocking drivers (`aiosqlite`).

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💡 Architectural Overview: What, Where, When, Why & How

* **What**: Asynchronous database integration layer using SQLAlchemy 2.0 AsyncEngine and non-blocking SQL drivers (`aiosqlite`, `asyncpg`).
* **Where**: Applied in data access objects (DAOs), repository layers, and ORM query handlers in FastAPI web apps.
* **When**: When executing SQL queries, transactions, or CRUD operations inside asynchronous applications.
* **Why**: Prevents database socket wait times from stalling the event loop, enabling thousands of concurrent HTTP requests while waiting for database queries.
* **How**: `create_async_engine()` creates a connection pool backed by non-blocking OS sockets. `AsyncSession` manages transactional scopes asynchronously.

---

## 📖 Theoretical Deep Dive

### 1. SQLAlchemy 2.0 Async Architecture

```text
                       SQLALCHEMY 2.0 ASYNC STACK
                                    |
+-------------------------------------------------------------------------+
|                  FastAPI / Async Application Coroutine                  |
+-------------------------------------------------------------------------+
                                    |
                                    v (await session.execute(stmt))
+-------------------------------------------------------------------------+
|                     AsyncSession (Session Factory)                      |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|               AsyncEngine (create_async_engine)                         |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|               aiosqlite Driver (Async Socket Interface)                 |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                          SQLite Database Engine                         |
+-------------------------------------------------------------------------+
```

---

## 🔬 Under the Hood: Async Sessions & Automatic Transaction Rollback

Using `async with session.begin():` manages transaction scope automatically:
1. `session.begin()` opens an explicit database transaction (`BEGIN TRANSACTION`).
2. If the enclosed `async with` block exits without uncaught exceptions, `COMMIT` is executed.
3. If an uncaught exception is raised inside the block, `ROLLBACK` is executed automatically, preserving database integrity.

---

## 💻 Script-by-Script Breakdown & Line-by-Line Guide

### 1. [`01_async_sqlalchemy_setup.py`](file:Asynchronous-Programming/12_async_db_sqlalchemy/01_async_sqlalchemy_setup.py)
* **Goal**: Set up an in-memory SQLite database and create tables asynchronously via `conn.run_sync(Base.metadata.create_all)`.
* **Key Concept**: Initializing async database engines and table schemas.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L23** | `create_async_engine("sqlite+aiosqlite:///:memory:")` | Instantiates non-blocking SQLite database engine. |
| **L31** | `await conn.run_sync(Base.metadata.create_all)` | Executes schema creation via synchronous dialect wrapper. |

---

### 2. [`02_async_crud_operations.py`](file:Asynchronous-Programming/12_async_db_sqlalchemy/02_async_crud_operations.py)
* **Goal**: Perform full asynchronous CRUD (Create, Read, Update, Delete) operations using `AsyncSession` and `select()`.
* **Key Concept**: Asynchronous ORM query execution.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L25** | `async_sessionmaker(engine, expire_on_commit=False)` | Session factory preventing implicit synchronous lazy-loading. |
| **L31** | `await session.execute(select(Product))` | Non-blockingly executes SQL query statement. |
| **L38** | `await session.commit()` | Commits active transaction asynchronously. |

---

### 3. [`03_transactions_and_sessions.py`](file:Asynchronous-Programming/12_async_db_sqlalchemy/03_transactions_and_sessions.py)
* **Goal**: Demonstrate automatic transaction rollback when an error occurs during an async DB session.
* **Key Concept**: Transactional safety and automatic rollback.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L26** | `async with session.begin():` | Transaction boundary issuing `BEGIN TRANSACTION` and auto `COMMIT`/`ROLLBACK`. |

---

## 🏃 Console Outputs & Benchmarks

### Running `02_async_crud_operations.py`:
```text
=== 1. CREATE: Inserting Async ORM Records ===
=== 2. READ: Querying Records Asynchronously ===
 -> Found Product #1: Laptop ($999.99)
 -> Found Product #2: Keyboard ($49.99)
=== 3. UPDATE: Modifying Price ===
=== 4. DELETE: Removing Record ===
Async DB CRUD Operations Completed Successfully!
```

---

## ❓ Exercises & Practical Knowledge Checks

1. **Question**: Why do we set `expire_on_commit=False` when creating `async_sessionmaker`?
   - **Answer**: In synchronous SQLAlchemy, accessing attributes on an expired ORM object triggers synchronous lazy-loading I/O. Setting `expire_on_commit=False` prevents implicit synchronous database access after a transaction commits.

2. **Practice Task**: Write an async function using `AsyncSession` that inserts 100 records in a single batch transaction using `session.add_all()`.

