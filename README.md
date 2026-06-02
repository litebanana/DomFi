# DomFi — Smart Budget App

A full-stack personal finance tracker with AI insights, built with React, Node.js, MongoDB, and Python AI.

---

## 📁 Project Structure

```
domfi/
├── frontend/          # React app (Vite)
├── backend/           # Node.js + Express API
├── ai/                # Python AI/Decision Tree service
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB (local or Atlas URI)

---

### 1. Backend (Node.js + Express + MongoDB)

```bash
cd backend
npm install
```

Create a `.env` file in `backend/`:
```
PORT=4000
MONGO_URI=mongodb://localhost:27017/domfi
ANTHROPIC_API_KEY=your_key_here
```

Start the backend:
```bash
npm run dev
```

---

### 2. AI Service (Python)

```bash
cd ai
pip install -r requirements.txt
python app.py
```

Runs on `http://localhost:5001`

---

### 3. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`

---

## ✨ Features

- **Onboarding** — First-run setup: enter your income, set category budgets from scratch
- **Dashboard** — Balance, income/expense stats, charts, AI insights
- **Transactions** — Add, filter, delete transactions (fully functional)
- **Budget Limits** — Set/edit/delete per-category budgets
- **Savings Goals** — Create goals, track progress, delete when done
- **Subscriptions** — Track recurring bills, add/remove subscriptions
- **AI Chat** — Ask Claude AI about your finances
- **Forecasting** — 6-month cash flow projection
- **Voice & OCR** — Simulated voice logging and receipt scanning
- **Pastel Theme** — Soft, aesthetic pastel UI with light/dark modes

## 🗄️ Database Schema (MongoDB)

Collections:
- `users` — profile & settings
- `transactions` — income/expense records
- `budgets` — category budget limits
- `goals` — savings goals
- `subscriptions` — recurring subscriptions

## 🤖 AI Service (Python)

The Python service at `ai/app.py` provides:
- `/analyze` — spending pattern analysis using a decision tree classifier
- `/forecast` — expense forecasting using linear regression
- `/categorize` — auto-categorize transactions

Claude AI (via Anthropic API) is called from the backend for the chat feature.
