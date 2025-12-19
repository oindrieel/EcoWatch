import sqlite3
import os


def create_database(db_name="sample_database.db"):
    """Creates a SQLite database with a sample schema and data."""

    # Remove existing file if it exists to start fresh
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Removed existing {db_name}")

    # Connect to the database (this will create the file)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    print(f"Connected to {db_name}...")

    # 1. Create Tables
    # ----------------
    print("Creating tables...")

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0
    )
    ''')

    # Create Orders table (showing relationships)
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
    # ---------------------
    print("Inserting sample data...")

    # Insert Users
    users = [
        ('alice_wonder', 'alice@example.com'),
        ('bob_builder', 'bob@example.com'),
        ('charlie_dev', 'charlie@example.com')
    ]
    cursor.executemany('INSERT INTO users (username, email) VALUES (?, ?)', users)

    # Insert Products
    products = [
        ('Laptop', 999.99, 10),
        ('Mouse', 25.50, 100),
        ('Keyboard', 45.00, 50),
        ('Monitor', 150.00, 30)
    ]
    cursor.executemany('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)', products)

    # Insert Orders (linking users and products)
    orders = [
        (1, 1, 1),  # Alice bought 1 Laptop
        (1, 2, 2),  # Alice bought 2 Mice
        (2, 3, 1),  # Bob bought 1 Keyboard
        (3, 1, 1),  # Charlie bought 1 Laptop
        (3, 4, 2)  # Charlie bought 2 Monitors
    ]
    cursor.executemany('INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)', orders)

    # Commit changes
    conn.commit()
    print("Data committed.")

    # 3. Verify Data
    # --------------
    print("\n--- Verifying Data: Order Summary ---")

    query = '''
    SELECT 
        u.username, 
        p.name AS product, 
        o.quantity, 
        (p.price * o.quantity) AS total_cost 
    FROM orders o
    JOIN users u ON o.user_id = u.id
    JOIN products p ON o.product_id = p.id
    ORDER BY u.username;
    '''

    rows = cursor.execute(query).fetchall()

    print(f"{'Username':<15} | {'Product':<15} | {'Qty':<5} | {'Total Cost'}")
    print("-" * 55)
    for row in rows:
        print(f"{row[0]:<15} | {row[1]:<15} | {row[2]:<5} | ${row[3]:.2f}")

    # Close connection
    conn.close()
    print(f"\nSuccess! SQLite file '{db_name}' is ready.")


if __name__ == "__main__":
    create_database()