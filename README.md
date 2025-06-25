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

🛠️ Getting Started

Backend Setup

# Clone backend
$ git clone https://github.com/YOUR-USERNAME/anchor-pos-backend.git
$ cd anchor-pos-backend

# Set up virtual environment
$ python -m venv env
$ source env/bin/activate

# Install dependencies
$ pip install -r requirements.txt

# Run server
$ uvicorn app.main:app --reload

Frontend Setup

# Clone frontend
$ git clone https://github.com/YOUR-USERNAME/anchor-pos-frontend.git
$ cd anchor-pos-frontend

# Install dependencies
$ npm install

# Run Vite dev server
$ npm run dev

🧾 Project Structure

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

🌟 Contributing

Pull requests and feedback are welcome! The goal is to make Anchor POS a powerful, extensible system for independent retailers across industries.

🧑‍💻 Author

Casey Ortiz🔗 linkedin.com/in/kco1 📫 kcarlos.ortiz@gmail.com

Anchor POS was built to empower local businesses with modern, intelligent retail tools.
Future enhancements will include multi-location support, AI assistant for analytics, and integrated payment terminals.
