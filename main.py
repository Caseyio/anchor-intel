# main.py

# ────────────────
# Standard library
# ────────────────
import os
import logging

# ────────────────
# Third-party packages
# ────────────────
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ────────────────
# Internal imports
# ────────────────
from app.core.logging_config import logger
from app.db.database import engine
from app.models.models import Base

# ────────────────
# Route imports
# ────────────────
from routes.users import router as users_router
from routes.products import router as products_router
from routes.sales import router as sales_router
from routes.inventory import router as inventory_router
from routes.analytics import router as analytics_router
from routes.alerts import router as alerts_router
from routes.auth_routes import router as auth_router
from routes.returns import router as returns_router
from routes.cashier_session import router as cashier_session_router
from routes.manager_closeout import router as manager_closeout_router
from routes.ai import router as ai_router

# ─────────────────────────────
# Logging Setup
# ─────────────────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# ─────────────────────────────
# Database Initialization
# ─────────────────────────────
# Base.metadata.create_all(bind=engine)  # Enable for local dev if needed

# ─────────────────────────────
# FastAPI Initialization
# ─────────────────────────────
app = FastAPI(
    title="Anchor POS API",
    description="Backend API for Anchor POS and Analytics Platform",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Route
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok"}


# ─────────────────────────────
# Router Registration
# ─────────────────────────────
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(products_router, prefix="/api/products", tags=["Products"])
app.include_router(sales_router, prefix="/api/sales", tags=["Sales"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(alerts_router)  # ✅ Prefix defined in alerts.py
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Assistant"])
app.include_router(returns_router, prefix="/api/returns", tags=["Returns"])
app.include_router(
    cashier_session_router, prefix="/api/cashier_sessions", tags=["Cashier Sessions"]
)
app.include_router(
    manager_closeout_router, prefix="/api/manager_closeouts", tags=["Manager Closeouts"]
)

logger.info("✅ FastAPI app initialized and routers registered.")
