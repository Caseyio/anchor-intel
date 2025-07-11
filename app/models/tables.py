# tables.py

from datetime import datetime
import sqlalchemy
from .database import metadata  # adjust if you're outside a package

# Tables
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.Text, unique=True, nullable=False),
    sqlalchemy.Column("password_hash", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("role", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime, default=datetime.utcnow),
    sqlalchemy.CheckConstraint("role IN ('admin', 'cashier')", name="users_role_check"),
)

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("sku", sqlalchemy.String(100), nullable=False, unique=True),
    sqlalchemy.Column("price", sqlalchemy.Numeric(10, 2), nullable=False),
    sqlalchemy.Column("category", sqlalchemy.String(100)),
    sqlalchemy.Column("stock_quantity", sqlalchemy.Integer, default=0),
)

sales = sqlalchemy.Table(
    "sales",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime, default=datetime.utcnow),
    sqlalchemy.Column("total_amount", sqlalchemy.Numeric(10, 2), nullable=False),
    sqlalchemy.Column(
        "updated_at",
        sqlalchemy.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    ),
)

sale_items = sqlalchemy.Table(
    "sale_items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "sale_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("sales.id", ondelete="CASCADE"),
    ),
    sqlalchemy.Column(
        "product_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id")
    ),
    sqlalchemy.Column("quantity", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("price", sqlalchemy.Numeric(10, 2), nullable=False),
)

inventory_events = sqlalchemy.Table(
    "inventory_events",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "product_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id")
    ),
    sqlalchemy.Column("change", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("reason", sqlalchemy.Text),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime, default=datetime.utcnow),
    sqlalchemy.Column(
        "updated_at",
        sqlalchemy.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    ),
)
