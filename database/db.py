"""
Database module for Marwan Management CRM
Handles SQLite database initialization, CRUD operations, and seed data
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "restaurant_crm.db")


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with tables and seed data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER DEFAULT 0,
            unit_price REAL DEFAULT 0
        )
    """)
    
    # Create waste table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            reason TEXT,
            date TEXT DEFAULT CURRENT_DATE
        )
    """)
    
    # Create assets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            purchase_date TEXT,
            value REAL DEFAULT 0,
            condition TEXT
        )
    """)
    
    conn.commit()
    
    # Check if database is empty and seed data
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        seed_data(cursor, conn)
    
    conn.close()


def seed_data(cursor, conn):
    """Seed database with sample FnB data"""
    # Sample products
    products = [
        ("Tomatoes", "Vegetables", 50, 2.50),
        ("Chicken Breast", "Meat", 30, 8.99),
        ("Olive Oil", "Oils & Condiments", 20, 12.00),
        ("Rice", "Grains", 100, 3.50),
        ("Onions", "Vegetables", 40, 1.75),
        ("Beef", "Meat", 25, 15.99),
        ("Pasta", "Grains", 60, 2.25),
        ("Cheese", "Dairy", 35, 6.50),
        ("Lettuce", "Vegetables", 30, 2.00),
        ("Bread", "Bakery", 50, 1.50),
        ("Milk", "Dairy", 40, 3.25),
        ("Eggs", "Dairy", 100, 4.50),
    ]
    
    cursor.executemany(
        "INSERT INTO products (name, category, quantity, unit_price) VALUES (?, ?, ?, ?)",
        products
    )
    
    # Sample waste entries
    waste_entries = [
        ("Tomatoes", 5, "Expired", "2025-11-10"),
        ("Lettuce", 3, "Damaged", "2025-11-11"),
        ("Bread", 10, "Stale", "2025-11-12"),
        ("Milk", 2, "Expired", "2025-11-10"),
        ("Onions", 4, "Damaged", "2025-11-11"),
        ("Chicken Breast", 1, "Expired", "2025-11-12"),
    ]
    
    cursor.executemany(
        "INSERT INTO waste (item, quantity, reason, date) VALUES (?, ?, ?, ?)",
        waste_entries
    )
    
    # Sample assets
    assets = [
        ("Commercial Refrigerator", "Equipment", "2023-01-15", 3500.00, "Good"),
        ("Industrial Oven", "Equipment", "2022-06-20", 8500.00, "Excellent"),
        ("Food Processor", "Equipment", "2024-03-10", 450.00, "Good"),
        ("Delivery Van", "Vehicle", "2021-09-05", 25000.00, "Fair"),
        ("POS System", "Technology", "2023-11-01", 1200.00, "Excellent"),
        ("Dishwasher", "Equipment", "2022-12-10", 2800.00, "Good"),
    ]
    
    cursor.executemany(
        "INSERT INTO assets (name, type, purchase_date, value, condition) VALUES (?, ?, ?, ?, ?)",
        assets
    )
    
    conn.commit()


# Products CRUD operations
def get_all_products() -> List[Dict]:
    """Get all products"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product(product_id: int) -> Optional[Dict]:
    """Get a single product by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(name: str, category: str, quantity: int, unit_price: float) -> int:
    """Add a new product"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, quantity, unit_price) VALUES (?, ?, ?, ?)",
        (name, category, quantity, unit_price)
    )
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id


def update_product(product_id: int, name: str, category: str, quantity: int, unit_price: float):
    """Update a product"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name = ?, category = ?, quantity = ?, unit_price = ? WHERE id = ?",
        (name, category, quantity, unit_price, product_id)
    )
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    """Delete a product"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


# Waste CRUD operations
def get_all_waste() -> List[Dict]:
    """Get all waste entries"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM waste ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_waste(waste_id: int) -> Optional[Dict]:
    """Get a single waste entry by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM waste WHERE id = ?", (waste_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_waste(item: str, quantity: int, reason: str, date: str = None):
    """Add a new waste entry"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO waste (item, quantity, reason, date) VALUES (?, ?, ?, ?)",
        (item, quantity, reason, date)
    )
    waste_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return waste_id


def update_waste(waste_id: int, item: str, quantity: int, reason: str, date: str):
    """Update a waste entry"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE waste SET item = ?, quantity = ?, reason = ?, date = ? WHERE id = ?",
        (item, quantity, reason, date, waste_id)
    )
    conn.commit()
    conn.close()


def delete_waste(waste_id: int):
    """Delete a waste entry"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM waste WHERE id = ?", (waste_id,))
    conn.commit()
    conn.close()


# Assets CRUD operations
def get_all_assets() -> List[Dict]:
    """Get all assets"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_asset(asset_id: int) -> Optional[Dict]:
    """Get a single asset by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_asset(name: str, type: str, purchase_date: str, value: float, condition: str) -> int:
    """Add a new asset"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO assets (name, type, purchase_date, value, condition) VALUES (?, ?, ?, ?, ?)",
        (name, type, purchase_date, value, condition)
    )
    asset_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return asset_id


def update_asset(asset_id: int, name: str, type: str, purchase_date: str, value: float, condition: str):
    """Update an asset"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE assets SET name = ?, type = ?, purchase_date = ?, value = ?, condition = ? WHERE id = ?",
        (name, type, purchase_date, value, condition, asset_id)
    )
    conn.commit()
    conn.close()


def delete_asset(asset_id: int):
    """Delete an asset"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()


# Summary/Statistics functions
def get_products_count() -> int:
    """Get total number of products"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_waste_quantity() -> int:
    """Get total waste quantity"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM waste")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_total_asset_value() -> float:
    """Get total asset value"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(value), 0) FROM assets")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_waste_by_reason() -> List[Tuple[str, int]]:
    """Get waste grouped by reason"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT reason, SUM(quantity) as total FROM waste GROUP BY reason ORDER BY total DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in rows]

