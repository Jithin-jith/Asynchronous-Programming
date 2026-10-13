"""
===============================================================================
Database Initialization Script for Asynchronous Programming Masterclass
===============================================================================
Creates 'ecommerce.db' with sample tables (users, products, orders, ai_logs)
and realistic seed data used across Modules 01 to 05.
===============================================================================
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "ecommerce.db"


def init_database():
    print(f"[Database Setup] Initializing SQLite database at: {DB_PATH.name}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'customer',
            status TEXT DEFAULT 'active'
        );
    """)

    # 2. Products Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        );
    """)

    # 3. Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    # 4. AI Query / Response Cache Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            model TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed Users
    users_data = [
        ("Alice Johnson", "alice@example.com", "admin", "active"),
        ("Bob Smith", "bob@example.com", "customer", "active"),
        ("Charlie Brown", "charlie@example.com", "customer", "pending"),
        ("Diana Prince", "diana@example.com", "premium", "active"),
        ("Evan Wright", "evan@example.com", "customer", "inactive"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO users (name, email, role, status)
        VALUES (?, ?, ?, ?)
    """, users_data)

    # Seed Products
    products_data = [
        ("AI Cloud Server", "Compute", 499.99, "High-performance GPU node for machine learning inference."),
        ("Vector Database License", "Software", 199.50, "Scalable vector index for semantic search and embeddings."),
        ("Async Framework Guide", "Education", 29.99, "Mastering asynchronous and event-driven architectures."),
        ("Edge IoT Gateway", "Hardware", 89.00, "Low-latency edge processor for real-time telemetry streaming."),
        ("LLM Prompt Optimizer", "Tools", 49.00, "Token compression and latency tuning utility for LLMs."),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO products (name, category, price, description)
        VALUES (?, ?, ?, ?)
    """, products_data)

    # Seed Orders
    orders_data = [
        (1, "AI Cloud Server", 2, 999.98, "completed"),
        (2, "Async Framework Guide", 1, 29.99, "completed"),
        (3, "Vector Database License", 1, 199.50, "pending"),
        (4, "Edge IoT Gateway", 3, 267.00, "completed"),
        (2, "LLM Prompt Optimizer", 1, 49.00, "processing"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO orders (user_id, product_name, quantity, total_amount, status)
        VALUES (?, ?, ?, ?, ?)
    """, orders_data)

    conn.commit()
    conn.close()
    print(f"[Database Setup] Successfully initialized tables and seed data in '{DB_PATH.name}'.")


if __name__ == "__main__":
    init_database()
