# Phase-Wise Codebase Map

This file maps implementation modules to phase goals from:
- `docx/problemstatment.md`
- `docx/tech-architecture.md`
- `docx/edgecase.md`

## Phase 1 (MVP Baseline)

### Responsibilities
- Data load + normalization
- Deterministic filtering (location, budget, cuisine, rating)
- Base recommendation API flow

### Code
- `src/phases/phase1/candidate_selector.py`
- `src/services/data_store.py`
- `src/models/schemas.py`
- `src/api/routes.py` (`POST /recommendations`, `GET /health`)

## Phase 2 (Quality + Reliability)

### Responsibilities
- Prompt template v2 and grounded output checks
- Fallback policy controls
- Observability improvements and evaluation harness

### Code
- `src/phases/phase2/quality_guardrails.py`
- `src/services/prompt_builder.py`
- `src/services/response_validator.py`
- `src/services/fallback_engine.py`
- `src/services/metrics.py` (`p50`, `p95`, avg latency)
- `scripts/evaluate_phase2.py`
- `tests/evaluation_cases.json`

## Phase 3 (Personalization + Scale Readiness)

### Responsibilities
- User preference memory
- Ranking signal persistence (feedback loop)
- Hybrid reranking

### Code
- `src/phases/phase3/user_memory.py`
- `src/phases/phase3/ranking_signals.py`
- `src/phases/phase3/hybrid_ranker.py`
- `src/services/recommender.py` (phase orchestration)
- `src/api/routes.py` (`POST /feedback`)

## Shared Runtime Entry

- `src/main.py` bootstraps all phases through `RecommenderService`.

## Phase 4 (Experience Layer - Web App)

### Responsibilities
- Responsive UI for all devices
- Form-based preference collection
- Recommendation display with explanations
- Feedback capture for ranking signal loop

### Code
- `frontend/src/App.jsx`
- `frontend/src/components/RecommendationCard.jsx`
- `frontend/src/phases/phase4/api.js`
- `frontend/src/App.css`
- `frontend/src/index.css`

## Phase 5 (Interactive UX + Free Deploy)

### Responsibilities
- Add interactive UX hooks (quick moods, surprise mode, streak)
- Ensure zero-cost default behavior
- Add free hosting deployment configs

### Code
- `frontend/src/phases/phase5/interaction.js`
- `render.yaml` (free backend deployment target)
- `frontend/vercel.json` (frontend deployment target)
- `streamlit_app.py` (free demo app deployment target)
