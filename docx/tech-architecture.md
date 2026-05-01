# Technical Architecture (Phase-Wise)

This document defines a clear, build-ready architecture for the AI-powered restaurant recommendation system described in `docx/problemstatment.md`.

---

## 1) Architecture Goals

- Deliver useful and explainable restaurant recommendations.
- Keep response time fast for interactive usage.
- Build with modular components so future upgrades are easy.
- Ensure recommendations stay grounded in dataset facts.

---

## 2) High-Level System Design

### Core Layers
1. **Experience Layer (UI)**
   - Collect user preferences.
   - Display ranked recommendations with explanations.

2. **Application Layer (Backend API)**
   - Validate request input.
   - Run deterministic filtering.
   - Call ranking and explanation services.
   - Return response in consistent schema.

3. **Intelligence Layer**
   - **Rule-based Candidate Selector** (hard constraints first).
   - **LLM Recommendation Engine** (ranking + short explanation).

4. **Data Layer**
   - Restaurant dataset store.
   - Optional feature store for ranking signals in later phases.
   - Logs/metrics storage for observability.

### End-to-End Request Flow
1. User submits preferences.
2. API validates and normalizes inputs.
3. Candidate Selector applies deterministic filters.
4. LLM ranks shortlisted candidates and generates reasons.
5. Response formatter returns top-N recommendations.
6. Logging layer captures latency, result quality signals, and fallbacks.

---

## 3) Suggested Tech Stack (Simple + Scalable)

- **Frontend**: React (or Next.js) + simple form UI.
- **Backend**: Python FastAPI (or Node.js Express).
- **Data Processing**: Pandas for ingestion and preprocessing.
- **Primary Storage (Phase 1/2)**: PostgreSQL or SQLite.
- **Search/Filtering**: SQL + indexed columns.
- **LLM Integration**: Provider SDK with prompt templates.
- **Observability**: Structured logs + basic metrics dashboard.
- **Deployment**: Docker + one cloud VM/container platform.

> Keep stack minimal in Phase 1. Add complexity only when needed.

---

## 4) Data Model (Minimum Required)

### `restaurants` table
- `restaurant_id` (primary key)
- `name`
- `city`
- `locality`
- `cuisines` (array/text)
- `avg_cost_for_two`
- `rating`
- `votes` (optional now, useful later)
- `metadata_json` (optional extra attributes)
- `updated_at`

### `recommendation_logs` table
- `request_id`
- `timestamp`
- `input_preferences_json`
- `candidate_count`
- `recommended_restaurant_ids`
- `latency_ms`
- `fallback_used` (boolean)
- `user_feedback` (optional in later phase)

---

## 5) API Contracts (Stable from Day 1)

### `POST /recommendations`
**Input**
- `location` (required)
- `budget` (required: low/medium/high or numeric range)
- `cuisine` (required)
- `min_rating` (required)
- `optional_preferences` (optional list)

**Output**
- `request_id`
- `recommendations`: list of:
  - `restaurant_name`
  - `cuisine`
  - `rating`
  - `estimated_cost`
  - `explanation`
- `meta`:
  - `candidate_count`
  - `processing_time_ms`
  - `fallback_used`

### `GET /health`
- Returns service health and dependency status.

### `GET /metrics` (internal)
- Basic counters and latency summaries.

---

## 6) Phase-Wise Architecture Plan

## Phase 1 - MVP (Functional Baseline)

### Scope
- Data ingestion and cleaning pipeline.
- Deterministic filtering by location, budget, cuisine, rating.
- Basic LLM ranking and explanation generation.
- Top-N recommendation UI/API output.

### Components to Build
1. **Ingestion Job**
   - Load dataset from source.
   - Normalize field names and value formats.
   - Handle missing values.

2. **Recommendation API**
   - Input validation and normalization.
   - Candidate selection query.
   - LLM prompt call.
   - Response formatter.

3. **Prompt Template v1**
   - Include only filtered restaurant candidates.
   - Ask for ranking + concise reason per item.
   - Instruct model to avoid unsupported claims.

4. **Basic Logging**
   - Request/response metadata.
   - Latency and error logs.

### Architecture Decision for Phase 1
- Keep everything in one backend service for speed.
- Use synchronous request flow.
- Use simple caching only if latency is high.

---

## Phase 2 - Quality and Reliability

### Scope
- Better recommendation quality and stronger explanations.
- Fallback handling when candidate set is small/empty.
- Improved observability and evaluation loop.

### New/Improved Components
1. **Prompt Template v2**
   - Better ranking criteria weighting.
   - Standardized explanation style (short, clear, factual).

2. **Fallback Engine**
   - If zero results: relax constraints in controlled order.
   - Example: lower min rating slightly, then expand locality radius.
   - Return why fallback was applied in `meta`.

3. **Quality Evaluator**
   - Offline checks on recommendation relevance.
   - Track precision-like metrics from test cases.

4. **Monitoring Upgrade**
   - p50/p95 latency.
   - API success/error rates.
   - Fallback frequency.

### Architecture Decision for Phase 2
- Keep filter logic and LLM logic separated into modules/services.
- Add configuration-driven ranking weights and fallback rules.

---

## Phase 3 - Scale and Personalization

### Scope
- User history and preference memory.
- Better ranking signals and personalization.
- Preparedness for larger dataset and traffic.

### New Components
1. **User Profile Service**
   - Store user preference history.
   - Build reusable preference vectors/tags.

2. **Ranking Signal Store**
   - Persist intermediate ranking features (clicks, saves, accepted recommendations).

3. **Hybrid Recommender**
   - Combine deterministic filters + learned ranking signals + LLM explanation.

4. **Performance Scaling**
   - Read replicas or managed DB scaling.
   - Caching hot queries.
   - Async jobs for heavy offline evaluations.

### Architecture Decision for Phase 3
- Split into multiple deployable services only when traffic/complexity requires.
- Keep API contract backward-compatible for frontend stability.

---

## 7) Recommendation Logic Design (Grounded and Explainable)

1. **Hard Constraints**
   - Must satisfy location and budget boundary.
   - Must satisfy minimum rating threshold (or fallback policy).

2. **Soft Ranking Signals**
   - Cuisine match strength.
   - Higher rating and vote confidence.
   - Optional preference match (family-friendly, quick service).

3. **LLM Responsibilities**
   - Re-rank top filtered candidates.
   - Generate user-friendly explanation text.
   - Do not invent missing restaurant facts.

4. **Guardrails**
   - LLM input restricted to known restaurant fields.
   - Output schema validation.
   - If invalid output, fallback to deterministic ranking response.

---

## 8) Performance and Reliability Strategy

- Add DB indexes on `city`, `cuisine`, `rating`, `avg_cost_for_two`.
- Limit candidate pool before LLM call (for cost and latency control).
- Use request timeout and retry policy for LLM failures.
- Return deterministic fallback if LLM is unavailable.
- Implement graceful no-result responses with suggestions.

---

## 9) Security and Safety Basics

- Validate and sanitize all user inputs.
- Rate limit public API endpoints.
- Keep API keys in environment variables, never in code.
- Log operational events without storing sensitive personal data.

---

## 10) Observability and Success Tracking

### Operational Metrics
- API latency (p50, p95)
- LLM call latency and error rate
- Fallback usage rate
- Empty-result rate

### Product Metrics (From Problem Statement)
- Recommendation relevance score
- Time to decision
- Sessions with at least one usable recommendation
- Explanation quality rating

---

## 11) Implementation Checklist by Phase

### Phase 1
- [ ] Dataset ingestion and schema normalization
- [ ] Basic recommendation API
- [ ] Deterministic filtering module
- [ ] LLM ranking + explanation module
- [ ] Top-N response formatter
- [ ] Basic logs and health endpoint

### Phase 2
- [ ] Prompt v2 and response quality rules
- [ ] Fallback rules engine
- [ ] Evaluation test suite and score tracking
- [ ] Metrics dashboard and alerts

### Phase 3
- [ ] User preference memory
- [ ] Hybrid ranking with behavior signals
- [ ] Scaled storage/caching strategy
- [ ] Offline model/ranking improvement loop

---

## 12) Non-Goals (Current Scope Control)

- No table booking or payment integration.
- No end-to-end review sentiment engine.
- No multilingual recommendation generation in initial versions.

This keeps the architecture focused, efficient, and aligned with the current milestone.

---

## 13) Implementation Update (Current Build)

This section reflects what is now implemented in code.

### Backend
- FastAPI service is active with endpoints:
  - `POST /recommendations`
  - `POST /feedback`
  - `GET /health`
  - `GET /metrics`
- CORS is enabled for local React frontend development.
- Data filtering, fallback ladder, prompt guardrails, and hybrid ranking are wired.

### LLM Integration
- LLM integration now calls a real OpenAI-compatible endpoint (Groq-style API path).
- API key source:
  - `LLM_API_KEY` from `.env` / environment only
- If LLM call fails, system falls back to deterministic explanations to keep reliability.

### Frontend (Experience Layer)
- React + Vite frontend added in `frontend/`.
- Modern responsive UI implemented for:
  - preference input
  - recommendation results
  - fallback notices
  - feedback actions (`Helpful` / `Not relevant`)
- Frontend integrates with backend endpoints and supports user-specific feedback loop.

### Phase Segregation (Code)
- `src/phases/phase1`: deterministic candidate selection
- `src/phases/phase2`: quality guardrails and fallback controls
- `src/phases/phase3`: user memory, ranking signals, hybrid ranker
- `frontend/src/phases/phase4`: experience-layer API integration for web UI

### Validation Workflow
- Backend tests run with `pytest`.
- Phase 2 evaluation script run with `python scripts/evaluate_phase2.py`.
- Frontend build validation run with `npm run build`.

---

## 14) UI Inspiration and Design Decision

- Reference platforms considered:
  - [Stitch by Google](https://stitch.withgoogle.com/)
  - [Godly](https://godly.website/)
- Current implementation uses a custom React UI inspired by modern product patterns.
- If current UX quality is already strong for usability/performance, we keep it and iterate incrementally.
- UI direction for this project:
  - clean cards and form workflow
  - interactive quick-mood chips
  - surprise mode
  - feedback-based engagement loop

---

## 15) Cost Strategy (Free-First)

- Default backend mode is now **`LLM_MODE=deterministic`**, so app runs at zero model cost.
- Remote paid/usage-based LLM calls are only enabled when explicitly setting `LLM_MODE=remote`.
- If remote LLM fails or is disabled, deterministic explanation fallback is always available.

---

## 16) Free Deployment Targets

### Backend (Free)
- Target: [Render](https://dashboard.render.com/)
- Config: `render.yaml`
- Plan: free web service

### Frontend (Free)
- Target: [Vercel](https://vercel.com/)
- Config: `frontend/vercel.json`
- Build: Vite static output (`dist`)

### Demo App (Free)
- Target: [Streamlit Cloud](https://share.streamlit.io/)
- Entry file: `streamlit_app.py`
- Useful for quick product demos without full frontend deployment dependency

---

## 17) New Phase Segregation

- **Phase 4**: frontend web experience layer (`frontend/src/phases/phase4`)
- **Phase 5**: interactive UX + free deployment readiness (`frontend/src/phases/phase5`, deploy configs)

---

## 18) Secret Management Update

- LLM key is now expected in `.env` via `LLM_API_KEY`.
- Original external key file flow is no longer required for normal runtime.
- Keep `.env` excluded from version control.
- Keep `LLM_MODE=deterministic` for free default execution; switch to `LLM_MODE=remote` only when remote LLM usage is intentionally enabled.

---

## 19) Localhost Full-App Validation (Completed)

End-to-end localhost checks were executed successfully:
- Backend tests: `pytest` passed.
- Backend API checks passed on `127.0.0.1:8000`:
  - `GET /health`
  - `POST /recommendations`
  - `POST /feedback`
- Frontend checks passed:
  - lint/build success
  - HTTP `200` from `http://127.0.0.1:5173`

This confirms full-stack local readiness for development and demo use.

---

## 20) Production Deployment Guide

### Backend Deployment on Render

#### Prerequisites
- Render account (free tier available)
- GitHub repository with the backend code

#### Steps
1. **Connect Repository to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Name: `restaurant-reco-backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: `Free`

3. **Environment Variables**
   - `LLM_MODE`: `deterministic` (for free deployment)
   - `DATA_FILE_PATH`: `data/restaurants_clean.csv`
   - `PYTHON_VERSION`: `3.9`

4. **Health Check**
   - Health Check Path: `/health`
   - Auto-Deploy: `Yes`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment (2-3 minutes)
   - Your backend URL will be: `https://restaurant-reco-backend.onrender.com`

#### Verification
```bash
curl https://restaurant-reco-backend.onrender.com/health
```

### Frontend Deployment on Vercel

#### Prerequisites
- Vercel account (free tier available)
- GitHub repository with the frontend code

#### Steps
1. **Connect Repository to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Connect your GitHub repository

2. **Configure Project**
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Environment Variables**
   - `VITE_API_BASE_URL`: `https://restaurant-reco-backend.onrender.com`

4. **Deploy**
   - Click "Deploy"
   - Wait for build and deployment (1-2 minutes)
   - Your frontend URL will be provided by Vercel

#### Verification
- Visit your Vercel URL
- Test the recommendation form
- Check browser console for any API errors

### Deployment Configuration Files

#### Backend (`render.yaml`)
```yaml
services:
  - type: web
    name: restaurant-reco-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: LLM_MODE
        value: deterministic
      - key: DATA_FILE_PATH
        value: data/restaurants_clean.csv
      - key: PYTHON_VERSION
        value: 3.9
    healthCheckPath: /health
    autoDeploy: yes
```

#### Frontend (`frontend/vercel.json`)
```json
{
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "env": {
    "VITE_API_BASE_URL": "https://restaurant-reco-backend.onrender.com"
  }
}
```

### API Configuration

The frontend automatically switches between local and production API URLs:
- **Local Development**: `http://127.0.0.1:8000`
- **Production**: `https://restaurant-reco-backend.onrender.com`

This is handled in `frontend/src/phases/phase4/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
```

### Post-Deployment Checklist

- [ ] Backend health endpoint responds correctly
- [ ] Frontend loads without errors
- [ ] Recommendation form works end-to-end
- [ ] Feedback submission works
- [ ] CORS is properly configured
- [ ] SSL certificates are active
- [ ] Error monitoring is set up (optional)

### Troubleshooting

#### Common Issues
1. **Backend 503 Error**: Check if data file exists and is accessible
2. **CORS Errors**: Verify frontend URL is in backend CORS allow list
3. **Build Failures**: Check logs for missing dependencies
4. **API Timeouts**: Render free tier has cold starts (first request may be slow)

#### Monitoring
- Render: Built-in metrics and logs
- Vercel: Build logs and analytics
- Consider adding uptime monitoring for production

### Cost Optimization
- Both platforms offer generous free tiers
- Backend runs on Render's free tier (750 hours/month)
- Frontend hosting is free on Vercel
- No additional costs with deterministic LLM mode
