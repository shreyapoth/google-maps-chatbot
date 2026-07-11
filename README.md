# Google Maps Chatbot

Minimal Flask + React scaffold for a maps-aware chatbot.

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Env

```bash
GOOGLE_MAPS_API_KEY=your-key
FRONTEND_ORIGIN=http://localhost:5173
VITE_API_URL=http://localhost:5000
```
