import sqlite3
import random
from datetime import datetime, timedelta
from src.db import get_db, init_db

PRODUCTS = ["Laptop", "Phone", "Tablet", "Headphones", "Camera", "Monitor"]
CUSTOMERS = ["Ali", "Sara", "Ahmed", "Fatima", "Usman", "Ayesha", "Bilal", "Hina"]

def seed_orders(count=200):
    """Seed the orders table with random data."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Clear existing data (safe to run twice)
    cursor.execute("DELETE FROM orders")
    
    # Insert random orders
    for _ in range(count):
        customer = random.choice(CUSTOMERS)
        product = random.choice(PRODUCTS)
        amount = round(random.uniform(5, 200), 2)
        days_ago = random.randint(0, 30)
        created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        cursor.execute(
            "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)",
            (customer, product, amount, created_at)
        )
    
    conn.commit()
    conn.close()
    print(f"Seeded {count} orders")

if __name__ == "__main__":
    init_db()
    seed_orders()
    
    # Verify count
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    conn.close()
    print(f" Total orders: {count}")