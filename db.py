import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "stok.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            location TEXT,
            note TEXT,
            created_at TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            type TEXT NOT NULL,            -- IN / OUT
            amount INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """
    )

    conn.commit()
    conn.close()


# -------------------- PRODUCTS --------------------

def add_product(code, name, category=None, quantity=0, location=None, note=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO products (code, name, category, quantity, location, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (code, name, category, quantity, location, note, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()


def update_product(product_id, **fields):
    if not fields:
        return

    keys = ", ".join([f"{k}=?" for k in fields.keys()])
    values = list(fields.values())
    values.append(product_id)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"UPDATE products SET {keys} WHERE id=?", values)

    conn.commit()
    conn.close()


def get_products(search=None):
    conn = get_connection()
    cur = conn.cursor()

    if search:
        cur.execute(
            """
            SELECT * FROM products
            WHERE code LIKE ? OR name LIKE ?
            ORDER BY name
            """,
            (f"%{search}%", f"%{search}%"),
        )
    else:
        cur.execute("SELECT * FROM products ORDER BY name")

    rows = cur.fetchall()
    conn.close()
    return rows


def get_product(product_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products WHERE id=?", (product_id,))
    row = cur.fetchone()

    conn.close()
    return row


# -------------------- STOCK MOVEMENTS --------------------

def stock_in(product_id, amount, description=None):
    _stock_move(product_id, amount, "IN", description)


def stock_out(product_id, amount, description=None):
    _stock_move(product_id, amount, "OUT", description)


def _stock_move(product_id, amount, move_type, description=None):
    if amount <= 0:
        raise ValueError("amount must be > 0")

    conn = get_connection()
    cur = conn.cursor()

    # current quantity
    cur.execute("SELECT quantity FROM products WHERE id=?", (product_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError("product not found")

    current_qty = row["quantity"]

    if move_type == "OUT" and current_qty < amount:
        conn.close()
        raise ValueError("insufficient stock")

    new_qty = current_qty + amount if move_type == "IN" else current_qty - amount

    # update product quantity
    cur.execute(
        "UPDATE products SET quantity=? WHERE id=?",
        (new_qty, product_id),
    )

    # insert movement
    cur.execute(
        """
        INSERT INTO stock_movements (product_id, type, amount, date, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (product_id, move_type, amount, datetime.now().isoformat(), description),
    )

    conn.commit()
    conn.close()


def get_movements(product_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM stock_movements
        WHERE product_id=?
        ORDER BY date DESC
        """,
        (product_id,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows
def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM stock_movements WHERE product_id=?",
        (product_id,)
    )
    count = cur.fetchone()[0]

    if count > 0:
        conn.close()
        raise ValueError("Stok hareketi olan ürün silinemez")

    cur.execute(
        "DELETE FROM products WHERE id=?",
        (product_id,)
    )

    conn.commit()
    conn.close()


# -------------------- QUICK TEST --------------------

if __name__ == "__main__":
    init_db()
    print("DB initialized at", DB_PATH)

