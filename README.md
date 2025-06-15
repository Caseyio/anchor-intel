# 🍾 Liquor Store POS Backend

A production-grade FastAPI backend for a full-featured liquor store POS (Point of Sale) system. Built with PostgreSQL, JWT-based auth, modular route structure, and integrated analytics.

## 🔧 Tech Stack

- **FastAPI** for async API development
- **PostgreSQL** via SQLAlchemy + Databases
- **Pydantic v2** for data validation
- **JWT Authentication** for secure access
- **Pytest + HTTPX** for async test coverage
- **Lifespan + Logging** for production readiness

## 🚀 Features

- 🔐 **User Auth**: Secure login with JWT, supports protected routes  
- 📦 **Inventory**: CRUD operations and stock management  
- 💸 **Sales**: Record sales, reduce stock, handle receipts  
- 📊 **Analytics**: Daily, weekly, and monthly revenue insights  
- ⚠️ **Alerts**: Real-time low-stock detection  
- 🧪 **Tests**: Async unit tests with full route coverage

## 🛠️ Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR-USERNAME/liquor-store-pos.git
   cd liquor-store-pos

liquor-store-pos/
├── app/                            # Main application package
│   ├── __init__.py
│   ├── main.py                     # FastAPI app with lifespan/startup/shutdown
│   ├── core/                       # Core config (logging, settings, etc.)
│   ├── db/                         # DB connection and database instance
│   ├── models/                     # Pydantic + SQLAlchemy models
│   ├── auth/                       # Authentication and dependencies
│   ├── routes/                     # All API route logic
│   └── utils/                      # Shared helpers (e.g. loggers, formatters)
├── tests/                          # All test files
├── scripts/                        # One-off or startup scripts
├── logs/                           # Log output
├── env/                            # Local dev virtualenv (should be in .gitignore)
├── requirements.txt               # Project dependencies
├── pyproject.toml                 # Project and test config
├── LICENSE                        # Software license
└── README.md                      # Project overview


Author
Casey Ortiz
