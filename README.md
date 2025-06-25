🧾 Anchor POS — Full Stack Retail POS System

Anchor POS is a full-featured Point of Sale system built for independent retailers, with a pilot implementation in liquor stores. It includes a robust FastAPI + PostgreSQL backend and a modern, responsive React + Tailwind frontend, supporting real-time inventory, receipts, returns, cashier sessions, and analytics.

📦 Tech Stack

Backend
* 🧠 FastAPI (Python 3.9)
* 🐘 PostgreSQL with SQLAlchemy ORM
* 🔐 JWT Auth via FastAPI Users
* 📄 Pydantic v2 models
* 🧪 Pytest + HTTPX for async tests
* 🧰 Structured logs, lifespan hooks, and environment config

Frontend
* ⚛️ React + Vite + Tailwind CSS
* 🔐 JWT login context with protected routes
* 🛒 Cart, payment modal, receipt rendering
* ⌨️ Keyboard-first cashier UX
* 🧾 Real-time receipt printing + return workflow

🚀 Features

🧠 Core
* Secure login with session caching
* POS cart + product search with autosuggest
* Print-friendly cashier and customer receipt views
* Product-level returns with refund, restock, and reason tracking

📦 Inventory & Sales
* Inventory CRUD and real-time adjustments
* Sale and return history with receipt lookup
* Product velocity + realized margin tracking

📊 Analytics (Backend Ready / Frontend Coming)
* Product efficiency score = margin × velocity
* Return rates by product/category
* Daily/weekly/monthly KPIs

💼 Cashier & Manager Tools (Planned)
* Cashier shift start/end flow with handoff
* Manager closeout report with:
   * Sales by cashier
   * Payment type breakdown (cash/card)
   * Ending cash balance vs. system total
   * Highlighted KPIs and anomalies

## 🧭 Project Milestones

The Anchor POS system is under continuous development. Key milestones include:

- ✅ Phase 1: Core POS features (checkout, returns, inventory, receipts)
- ✅ Phase 2: Cashier-friendly UI with keyboard-first UX
- ✅ Phase 3: Real-time receipt search & printing
- ✅ Phase 4: Inventory-aware analytics and product performance metrics
- 🔄 Phase 5: Cashier/Manager Closeout Workflow (In Progress)
- 🔜 Phase 6: AI Assistant Integration for Smart Queries and Charts
- 🔜 Phase 7: Cloud sync & multi-terminal support🧾 Project Structure

## 🧱 System Architecture

The Anchor POS system follows a modular architecture:

![Anchor POS Architecture](./assets/anchor-pos-architecture.png)

Backend: anchor-pos-backend

├── app/
│   ├── main.py
│   ├── auth/
│   ├── models/
│   ├── routes/
│   ├── db/
│   ├── core/
│   └── utils/
├── tests/
├── scripts/
├── requirements.txt
├── pyproject.toml
└── README.md

Frontend: anchor-pos-frontend

├── src/
│   ├── components/
│   ├── context/
│   ├── hooks/
│   ├── pages/
│   ├── App.jsx
│   └── main.jsx
├── public/
├── index.html
├── package.json
└── README.md

## 🔒 Source Code

The source code for this project is proprietary and not publicly available.

For a live demo or collaboration inquiry, please contact:

Casey Ortiz🔗 linkedin.com/in/kco1 📫 kcarlos.ortiz@gmail.com

Anchor POS was built to empower local businesses with modern, intelligent retail tools.
Future enhancements will include multi-location support, AI assistant for analytics, and integrated payment terminals.
