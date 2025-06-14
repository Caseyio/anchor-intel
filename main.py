# main.py
# Standard library
import os
import logging

# Third-party packages
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import database

from routes.users import router as users_router
from routes.products import router as products_router
from routes.sales import router as sales_router
from routes.inventory import router as inventory_router
from routes.analytics import router as analytics_router
from routes.alerts import router as alerts_router

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
# FastAPI Initialization
# ─────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# ─────────────────────────────
# Router Registration
# ─────────────────────────────
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(sales_router, prefix="/sales", tags=["Sales"])
app.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])


logger.info("✅ FastAPI app initialized and routers registered.")
