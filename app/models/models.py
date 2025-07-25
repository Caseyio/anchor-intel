# app/models/models.py

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


# ✅ Tenants Table
class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="tenant")
    products = relationship("Product", back_populates="tenant")
    sales = relationship("Sale", back_populates="tenant")
    returns = relationship("Return", back_populates="tenant")
    inventory_events = relationship("InventoryEvent", back_populates="tenant")
    cashier_sessions = relationship("CashierSession", back_populates="tenant")


# ✅ Users Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))

    tenant = relationship("Tenant", back_populates="users")

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'cashier')", name="users_role_check"),
    )


# ✅ Products Table
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False, unique=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100))
    stock_quantity = Column(Integer, default=0)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))

    tenant = relationship("Tenant", back_populates="products")

    sale_items = relationship(
        "SaleItem", back_populates="product", cascade="all, delete"
    )
    inventory_events = relationship(
        "InventoryEvent", back_populates="product", cascade="all, delete"
    )
    returns = relationship("Return", back_populates="product", cascade="all, delete")


# ✅ Sales Table
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    payment_type = Column(String, nullable=False)

    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))

    cashier = relationship("User")
    tenant = relationship("Tenant", back_populates="sales")

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete")
    returns = relationship("Return", back_populates="sale", cascade="all, delete")


# ✅ Sale Items Table
class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


# ✅ Inventory Events Table
class InventoryEvent(Base):
    __tablename__ = "inventory_events"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    change = Column(Integer, nullable=False)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))

    product = relationship("Product", back_populates="inventory_events")
    tenant = relationship("Tenant", back_populates="inventory_events")


# ✅ Returns Table
class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    product_id = Column(Integer, ForeignKey("products.id"))
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=True)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    notes = Column(Text)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))

    product = relationship("Product", back_populates="returns")
    sale = relationship("Sale", back_populates="returns")
    tenant = relationship("Tenant", back_populates="returns")


# ✅ Cashier Sessions
class CashierSession(Base):
    __tablename__ = "cashier_sessions"

    id = Column(Integer, primary_key=True)
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    terminal_id = Column(String, nullable=True)

    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    opening_cash = Column(Numeric(10, 2), nullable=False)
    closing_cash = Column(Numeric(10, 2), nullable=True)
    system_cash_total = Column(Numeric(10, 2), nullable=True)
    cash_difference = Column(Numeric(10, 2), nullable=True)
    is_over_short = Column(Boolean, default=False)

    notes = Column(Text)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))

    cashier = relationship("User")
    tenant = relationship("Tenant", back_populates="cashier_sessions")
