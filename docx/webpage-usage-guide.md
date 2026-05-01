# Webpage Usage Guide

This guide explains how to use the restaurant recommendation web app based on the goals in `docx/problemstatment.md`.

---

## 1) What This Web App Does

The app helps users quickly decide where to eat by:
- collecting preferences (location, budget, cuisine, rating, optional needs)
- filtering restaurants using structured rules
- generating explainable recommendations
- allowing feedback to improve future ranking

---

## 2) Start the Application Locally

## Backend
Run from project root:

```powershell
& "C:\Users\akshi\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

## Frontend
Run in `frontend/`:

```powershell
& "C:\Program Files\nodejs\npm.cmd" run dev -- --host 127.0.0.1 --port 5173
```

Open:
- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/health`

---

## 3) How to Use the Page

1. Open the form in the web app.
2. Enter:
   - `User ID` (optional but useful for personalization)
   - `Location` (city or locality)
   - `Budget` (`low`, `medium`, `high` or custom range style supported by backend)
   - `Cuisine`
   - `Min Rating` (0 to 5)
   - `Top N` results
   - Optional preferences (comma separated)
3. Click **Get Recommendations**.
4. Review recommendation cards:
   - restaurant name
   - cuisine
   - rating
   - estimated cost
   - explanation
5. Use feedback buttons:
   - **Helpful**
   - **Not relevant**

Feedback updates phase-3 ranking signals.

---

## 4) Interactive Features

- **Quick Mood chips** auto-fill preferences for common intents.
- **Surprise Me** applies a random mood configuration.
- **Discovery streak** increments when you successfully fetch recommendations.
- **Fallback notice** appears when strict filters return no direct results and fallback logic is used.

---

## 5) Expected Behaviors

- If no strong match exists, app applies fallback and still tries to provide useful options.
- If LLM remote mode is off/fails, deterministic recommendation logic keeps output stable.
- UI remains responsive for desktop and mobile widths.

---

## 6) Troubleshooting

- Backend not reachable:
  - verify backend server is running on port `8000`
- Frontend not loading:
  - verify frontend dev server is running on port `5173`
- No recommendations:
  - lower minimum rating
  - broaden location/cuisine
  - use mood chips for defaults

---

## 7) API Endpoints Used by Webpage

- `GET /health`
- `POST /recommendations`
- `POST /feedback`
- `GET /metrics` (internal monitoring)
