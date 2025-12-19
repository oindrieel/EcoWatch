import sqlite3
import sys

DB_NAME = "sample_database.db"


def get_connection():
    """Connects to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def initialize_database(conn):
    """
    Checks if the database is empty and creates the necessary tables
    and sample data if they are missing.
    """
    cursor = conn.cursor()

    # Check if 'products' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    if cursor.fetchone():
        return  # Tables already exist, no need to do anything

    print("--- Initializing Database (First Run Detected) ---")

    # 1. Create Tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # 2. Insert Sample Data
    print("Seeding sample data...")
    users = [
        ('alice_wonder', 'alice@example.com'),
        ('bob_builder', 'bob@example.com'),
        ('charlie_dev', 'charlie@example.com')
    ]
    cursor.executemany('INSERT INTO users (username, email) VALUES (?, ?)', users)

    products = [
        ('Laptop', 999.99, 10),
        ('Mouse', 25.50, 100),
        ('Keyboard', 45.00, 50),
        ('Monitor', 150.00, 30)
    ]
    cursor.executemany('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)', products)

    # Insert Orders (assuming IDs 1, 2, 3 generated in order)
    orders = [
        (1, 1, 1), (1, 2, 2), (2, 3, 1), (3, 1, 1), (3, 4, 2)
    ]
    cursor.executemany('INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)', orders)

    conn.commit()
    print("--- Database Initialized Successfully ---\n")


def list_products(conn):
    """Lists all products and their current stock."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM products")
    products = cursor.fetchall()

    print("\n--- Current Inventory ---")
    print(f"{'ID':<5} | {'Name':<15} | {'Price':<10} | {'Stock':<5}")
    print("-" * 45)
    for p in products:
        print(f"{p['id']:<5} | {p['name']:<15} | ${p['price']:<9.2f} | {p['stock']:<5}")


def place_order(conn, username, product_name, quantity):
    """
    Places an order safely using a transaction.
    Checks stock levels before confirming.
    """
    print(f"\n--- Processing Order: {username} wants {quantity} x {product_name} ---")
    cursor = conn.cursor()

    try:
        # Start transaction implicitly

        # 1. Get User ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            raise ValueError(f"User '{username}' not found.")
        user_id = user['id']

        # 2. Get Product ID and Stock
        cursor.execute("SELECT id, price, stock FROM products WHERE name = ?", (product_name,))
        product = cursor.fetchone()
        if not product:
            raise ValueError(f"Product '{product_name}' not found.")

        if product['stock'] < quantity:
            raise ValueError(f"Insufficient stock for {product_name}. Only {product['stock']} available.")

        # 3. Create Order
        cursor.execute('''
            INSERT INTO orders (user_id, product_id, quantity) 
            VALUES (?, ?, ?)
        ''', (user_id, product['id'], quantity))

        # 4. Update Stock
        new_stock = product['stock'] - quantity
        cursor.execute('UPDATE products SET stock = ? WHERE id = ?', (new_stock, product['id']))

        conn.commit()
        total_price = product['price'] * quantity
        print(f"✅ Success! Order placed for ${total_price:.2f}. New stock: {new_stock}")

    except (sqlite3.Error, ValueError) as e:
        conn.rollback()
        print(f"❌ Transaction Failed: {e}")


def get_sales_report(conn):
    """Generates a simple revenue report by product."""
    print("\n--- Sales Report (Revenue by Product) ---")
    query = '''
    SELECT 
        p.name, 
        SUM(o.quantity) as total_sold,
        SUM(o.quantity * p.price) as revenue
    FROM orders o
    JOIN products p ON o.product_id = p.id
    GROUP BY p.name
    ORDER BY revenue DESC
    '''
    cursor = conn.cursor()
    rows = cursor.execute(query).fetchall()

    print(f"{'Product':<15} | {'Units Sold':<10} | {'Revenue'}")
    print("-" * 40)
    for row in rows:
        print(f"{row['name']:<15} | {row['total_sold']:<10} | ${row['revenue']:.2f}")


def main():
    conn = get_connection()

    # --- FIX: Ensure DB is initialized before using it ---
    initialize_database(conn)

    # 1. Show initial state
    list_products(conn)

    # 2. Attempt a valid order
    place_order(conn, "alice_wonder", "Keyboard", 2)

    # 3. Attempt an invalid order (not enough stock)
    # Note: 'Laptop' usually has low stock from the generator script
    place_order(conn, "bob_builder", "Laptop", 50)

    # 4. Attempt an order for a non-existent user
    place_order(conn, "fake_user_123", "Mouse", 1)

    # 5. Show final report
    get_sales_report(conn)

    conn.close()


if __name__ == "__main__":
    main()