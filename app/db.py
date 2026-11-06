from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

if settings.database_url.startswith("sqlite"):
    Path("./data").mkdir(exist_ok=True)
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    statements = [
        """CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY, name TEXT, email TEXT, city TEXT, signup_date DATE, segment TEXT)""",
        """CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT, unit_price REAL, cost_price REAL)""",
        """CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY, customer_id TEXT, product_id TEXT, order_date DATE,
        quantity INTEGER, unit_price REAL, discount REAL DEFAULT 0, status TEXT)""",
        """CREATE TABLE IF NOT EXISTS tickets (
        ticket_id TEXT PRIMARY KEY, customer_id TEXT, created_at DATE, category TEXT,
        priority TEXT, sentiment TEXT, status TEXT, message TEXT)"""
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)"))
