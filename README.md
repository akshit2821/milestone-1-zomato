# Restaurant Recommendation System (Phase-Wise Full Stack)

This repository contains the Phase 1 implementation aligned with:
- `docx/problemstatment.md`
- `docx/tech-architecture.md`
- `docx/edgecase.md`

## What Is Implemented in Phase 1

- FastAPI backend with:
  - `GET /health`
  - `GET /metrics`
  - `POST /recommendations`
- Deterministic candidate filtering:
  - location, budget, cuisine, min rating
- Controlled fallback behavior for no-result strict filters
- LLM-ready ranking module (Phase 1 uses deterministic explanation generator)
- Data ingestion script for cleaning and normalizing restaurant data

## What Is Implemented in Phase 2

- Prompt template v2 (`src/services/prompt_builder.py`) to enforce grounded explanations
- Output schema validator (`src/services/response_validator.py`)
- Configurable fallback ladder (`src/services/fallback_engine.py`)
- Upgraded internal metrics with average and p50/p95 latency (`GET /metrics`)
- Basic evaluation harness and scored test cases:
  - `tests/evaluation_cases.json`
  - `scripts/evaluate_phase2.py`

## What Is Implemented in Phase 3

- User preference memory store:
  - `src/phases/phase3/user_memory.py`
- Ranking signal store for feedback-based score adjustments:
  - `src/phases/phase3/ranking_signals.py`
- Hybrid ranking stage combining base score + learned signal + cuisine bonus:
  - `src/phases/phase3/hybrid_ranker.py`
- New feedback API endpoint:
  - `POST /feedback`
- Optional `user_id` in recommendation payload for preference memory.

## What Is Implemented in Phase 4 (Frontend Experience Layer)

- React + Vite frontend in `frontend/`
- Modern responsive recommendation UI
- Device-friendly preference form and result cards
- Feedback buttons wired to backend `POST /feedback`

## What Is Implemented in Phase 5 (Interactive + Free Deploy)

- Interactive frontend controls:
  - Quick mood chips
  - Surprise mode
  - Discovery streak indicator
- Free-first backend behavior via `LLM_MODE=deterministic`
- Deployment configs added:
  - `render.yaml` (backend)
  - `frontend/vercel.json` (frontend)
  - `streamlit_app.py` (demo deployment)

## Project Structure

- `src/main.py` - FastAPI app bootstrap
- `src/api/routes.py` - HTTP routes
- `src/models/schemas.py` - request/response contracts
- `src/services/data_store.py` - shared data store and filtering base
- `src/services/recommender.py` - orchestrator across phases
- `src/services/llm_client.py` - recommendation generator
- `src/services/metrics.py` - in-memory operational metrics
- `src/phases/phase1/candidate_selector.py` - Phase 1 deterministic candidate selection
- `src/phases/phase2/quality_guardrails.py` - Phase 2 quality guardrails
- `src/phases/phase3/user_memory.py` - Phase 3 user preference memory
- `src/phases/phase3/ranking_signals.py` - Phase 3 ranking feedback signals
- `src/phases/phase3/hybrid_ranker.py` - Phase 3 hybrid reranking
- `frontend/src/App.jsx` - responsive web app shell
- `frontend/src/phases/phase4/api.js` - backend API integration for frontend
- `frontend/src/phases/phase5/interaction.js` - interactive UX controls
- `streamlit_app.py` - streamlit demo app
- `render.yaml` - render deployment config
- `frontend/vercel.json` - vercel deployment config
- `scripts/ingest_data.py` - raw dataset to clean dataset converter
- `scripts/evaluate_phase2.py` - evaluation runner for recommendation quality checks
- `data/restaurants_clean.csv` - sample cleaned dataset

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Run

```bash
uvicorn src.main:app --reload
```

Server URL: `http://127.0.0.1:8000`

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://127.0.0.1:5173`

Streamlit demo:

```bash
streamlit run streamlit_app.py
```

## API Example

`POST /recommendations`

```json
{
  "user_id": "user-123",
  "location": "Delhi",
  "budget": "medium",
  "cuisine": "chinese",
  "min_rating": 4.0,
  "optional_preferences": ["quick service"],
  "top_n": 5
}
```

`POST /feedback`

```json
{
  "user_id": "user-123",
  "restaurant_name": "Dragon Bowl",
  "score_delta": 0.5
}
```

## Notes

- Set `LLM_API_KEY` in `.env` when enabling remote LLM mode.
- Keep `LLM_MODE=deterministic` for fully free operation.
- To use real dataset ingestion, place source file as `data/restaurants_raw.csv` and run:

```bash
python scripts/ingest_data.py
```
