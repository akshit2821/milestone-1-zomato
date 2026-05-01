# Edge Cases and Mitigation Plan

This document lists critical edge cases for the restaurant recommendation web app and defines how to **prevent**, **detect**, and **recover** from them.

It is aligned with:
- `docx/problemstatment.md`
- `docx/tech-architecture.md`

Goal: deliver a fully fledged, reliable web app that works across devices, networks, and diverse user scenarios.

---

## 1) Edge-Case Strategy

For every edge case, we use this rule:
1. **Prevent** - reduce probability with validation, constraints, and good defaults.
2. **Detect** - monitor with logs, metrics, and alerts.
3. **Recover** - provide fallback behavior so user still gets usable output.

---

## 2) User Input Edge Cases

### 2.1 Missing Required Fields
- **Example**: user skips location or budget.
- **Risk**: backend returns poor matches or fails.
- **Prevent**: strict frontend + backend validation.
- **Recover**: inline form error messages; disable submit until valid.

### 2.2 Invalid Rating Values
- **Example**: `min_rating = 9` or negative values.
- **Risk**: impossible filters, empty results.
- **Prevent**: constrain range (for example 0 to 5).
- **Recover**: auto-correct to nearest valid bound with warning.

### 2.3 Ambiguous Location
- **Example**: user enters "Sector 12" without city.
- **Risk**: wrong city matching.
- **Prevent**: structured location input (`city`, `locality`).
- **Recover**: ask user to confirm location before recommendation call.

### 2.4 Budget Ambiguity
- **Example**: "cheap", "normal", "affordable".
- **Risk**: inconsistent filtering.
- **Prevent**: map labels to numeric ranges.
- **Recover**: apply default range and show selected mapping.

### 2.5 Contradictory Preferences
- **Example**: very low budget + very high minimum rating + rare cuisine.
- **Risk**: no candidates.
- **Prevent**: pre-submit warning for restrictive combinations.
- **Recover**: fallback engine relaxes constraints in controlled order.

### 2.6 Duplicate or Spam Requests
- **Example**: user clicks submit multiple times.
- **Risk**: extra LLM cost and duplicate processing.
- **Prevent**: disable submit button during in-flight request.
- **Recover**: idempotency key and request deduplication.

---

## 3) Data Ingestion and Quality Edge Cases

### 3.1 Missing Core Fields in Dataset
- **Example**: null `rating` or `avg_cost_for_two`.
- **Risk**: ranking noise and runtime errors.
- **Prevent**: ingestion validation rules and null handling policy.
- **Recover**: exclude broken rows or fill with safe defaults.

### 3.2 Inconsistent Cuisine Naming
- **Example**: "North Indian", "North-Indian", "N. Indian".
- **Risk**: poor filter match rate.
- **Prevent**: cuisine normalization dictionary at ingestion.
- **Recover**: fuzzy matching fallback in filter layer.

### 3.3 Duplicate Restaurants
- **Example**: same restaurant appears multiple times.
- **Risk**: repeated recommendations.
- **Prevent**: deduplication key (`name + locality + city`).
- **Recover**: remove duplicates in candidate list before LLM call.

### 3.4 Outdated Data
- **Example**: closed restaurants still in dataset.
- **Risk**: user trust drop.
- **Prevent**: periodic refresh job and `updated_at` checks.
- **Recover**: allow user report action and suppress flagged records.

### 3.5 Invalid Cost or Rating Formats
- **Example**: cost as text or rating as malformed string.
- **Risk**: query errors and bad sorting.
- **Prevent**: schema casting during ETL with reject logs.
- **Recover**: quarantine invalid rows and continue pipeline.

---

## 4) Candidate Selection Edge Cases

### 4.1 Zero Candidates After Filtering
- **Risk**: empty response and poor UX.
- **Prevent**: pre-check strictness score before executing query.
- **Recover**: fallback sequence:
  1. Reduce `min_rating` slightly.
  2. Expand locality to city level.
  3. Broaden cuisine to related categories.
  4. Return "closest matches" with explanation.

### 4.2 Too Many Candidates
- **Risk**: slow LLM calls and high token cost.
- **Prevent**: cap shortlist size (for example top 30 by deterministic score).
- **Recover**: two-step ranking (fast pre-rank, then LLM rerank).

### 4.3 Bias Toward Popular Restaurants
- **Risk**: same restaurants always shown.
- **Prevent**: blend diversity score into pre-ranking.
- **Recover**: apply diversity constraints in final top-N.

---

## 5) LLM Edge Cases

### 5.1 Hallucinated Explanations
- **Example**: model says "live music" when not in data.
- **Risk**: misinformation and trust loss.
- **Prevent**: prompt with strict "use only provided fields."
- **Recover**: output validator rejects unsupported claims and falls back.

### 5.2 Invalid Output Format
- **Example**: missing fields in response.
- **Risk**: API response parsing failure.
- **Prevent**: schema-constrained generation.
- **Recover**: retry once with stricter prompt, else deterministic response.

### 5.3 LLM Timeout or Provider Outage
- **Risk**: failed recommendation request.
- **Prevent**: timeout budget and provider health checks.
- **Recover**: deterministic ranking + templated explanations.

### 5.4 High LLM Latency
- **Risk**: poor interactive experience.
- **Prevent**: limit candidate tokens and prompt size.
- **Recover**: asynchronous response option + loading status + cached results.

### 5.5 Cost Spike
- **Risk**: budget overrun.
- **Prevent**: token budget caps, quota controls, caching by similar queries.
- **Recover**: switch to smaller model or deterministic-only mode temporarily.

---

## 6) API and Backend Edge Cases

### 6.1 Invalid API Payload
- **Risk**: 500 errors or undefined behavior.
- **Prevent**: strict request schema validation.
- **Recover**: return clear `400` with field-level messages.

### 6.2 Partial Service Failure
- **Example**: DB healthy, LLM down.
- **Risk**: endpoint instability.
- **Prevent**: dependency health checks.
- **Recover**: graceful degradation to non-LLM recommendation mode.

### 6.3 Traffic Spikes
- **Risk**: service slowdown and timeouts.
- **Prevent**: rate limiting and autoscaling thresholds.
- **Recover**: queue overflow protection + temporary traffic shaping.

### 6.4 Cache Poisoning or Stale Cache
- **Risk**: wrong recommendations.
- **Prevent**: cache key includes normalized preferences + version.
- **Recover**: TTL expiry + manual cache purge endpoint (internal).

### 6.5 Concurrency Race Issues
- **Risk**: inconsistent logs or duplicated writes.
- **Prevent**: request IDs and idempotent logging writes.
- **Recover**: transactional writes for critical records.

---

## 7) Frontend, UX, and Device Edge Cases

### 7.1 Mobile Layout Breaks
- **Risk**: unusable interface on smaller screens.
- **Prevent**: responsive breakpoints and touch-friendly controls.
- **Recover**: mobile-first fallback layout and progressive enhancement.

### 7.2 Slow/Unstable Network
- **Risk**: failed or hanging requests.
- **Prevent**: request timeout and retry policy.
- **Recover**: offline/poor network banner + retry CTA + last successful result cache.

### 7.3 Browser Compatibility
- **Risk**: failures on older browsers/devices.
- **Prevent**: supported browser policy + polyfills where needed.
- **Recover**: graceful degradation for non-critical features.

### 7.4 Session Loss During Use
- **Risk**: user loses selected filters.
- **Prevent**: local state persistence (`localStorage` or equivalent).
- **Recover**: restore last valid query on reload.

### 7.5 Long Explanation Text Overflow
- **Risk**: poor readability and broken cards.
- **Prevent**: character limit and standard explanation template.
- **Recover**: text clamp with "read more."

---

## 8) Accessibility and Inclusive UX Edge Cases

### 8.1 Keyboard-Only Navigation Failure
- **Risk**: inaccessible for many users.
- **Prevent**: full tab order and visible focus states.
- **Recover**: accessibility audit before release.

### 8.2 Screen Reader Issues
- **Risk**: recommendation cards not understandable.
- **Prevent**: semantic HTML, ARIA labels, landmark regions.
- **Recover**: manual screen reader QA in release checklist.

### 8.3 Low Vision and Contrast Problems
- **Risk**: unreadable UI.
- **Prevent**: WCAG-compliant contrast and scalable font sizes.
- **Recover**: accessibility theme toggles and contrast-safe palette.

### 8.4 Color-Only Status Signals
- **Risk**: inaccessible information.
- **Prevent**: always pair color with text/icon.
- **Recover**: accessibility linting checks in CI.

---

## 9) Security and Abuse Edge Cases

### 9.1 Injection Attacks (Input/Prompt/API)
- **Risk**: corrupted logic or data leaks.
- **Prevent**: sanitize all inputs, parameterized DB queries, prompt hardening.
- **Recover**: block suspicious payloads and log security events.

### 9.2 API Key Leakage
- **Risk**: unauthorized LLM usage.
- **Prevent**: server-only secrets and rotated keys.
- **Recover**: revoke compromised key and rotate immediately.

### 9.3 Bot Abuse and Scraping
- **Risk**: cost and performance degradation.
- **Prevent**: rate limiting, abuse detection, and bot challenge controls.
- **Recover**: dynamic throttling and IP/device reputation rules.

### 9.4 Sensitive Data in Logs
- **Risk**: privacy non-compliance.
- **Prevent**: structured logging with redaction rules.
- **Recover**: log purge procedures and audit trail.

---

## 10) Observability and Monitoring Edge Cases

### 10.1 Silent Failures
- **Risk**: broken app with no alert.
- **Prevent**: error budgets and alerting for key endpoints.
- **Recover**: runbook-based incident handling.

### 10.2 Metric Blind Spots
- **Risk**: cannot diagnose relevance or latency drops.
- **Prevent**: track operational + product metrics from day one.
- **Recover**: add instrumentation to missing areas quickly.

### 10.3 Missing Traceability
- **Risk**: hard to debug user complaints.
- **Prevent**: request IDs from UI to backend to logs.
- **Recover**: searchable logs by request ID.

---

## 11) Device and Platform Readiness Matrix

Minimum support targets:
- **Mobile**: Android Chrome, iOS Safari (latest major versions)
- **Desktop**: Chrome, Edge, Firefox, Safari (latest major versions)
- **Tablet**: iPadOS Safari, Android Chrome

Device readiness checklist:
- [ ] Responsive layout at common breakpoints (320px to 1440px+)
- [ ] Touch target size and spacing are mobile-friendly
- [ ] Form inputs usable with virtual keyboards
- [ ] Recommendation cards remain readable on small screens
- [ ] API interaction remains stable on low bandwidth
- [ ] Core flow works without animations or advanced effects

---

## 12) Edge Cases by Phase (Execution Plan)

## Phase 1 - Must Handle Before MVP Launch
- Input validation failures
- Missing/invalid dataset fields
- Zero-candidate fallback
- LLM timeout/failure fallback
- Basic mobile responsiveness
- Basic accessibility (keyboard + semantic structure)
- Basic security (input sanitization, secret management)

## Phase 2 - Reliability and Quality Hardening
- Controlled fallback ladder and user messaging
- Explanation grounding validation
- Better observability and alerting
- Browser compatibility hardening
- Abuse/rate-limit reinforcement
- Accessibility improvements (contrast, screen reader QA)

## Phase 3 - Scale and Personalization Hardening
- Traffic spikes and scaling controls
- Personalization edge cases (cold start, profile drift)
- Ranking bias checks
- Cost protection controls under high load
- Advanced monitoring and incident runbooks

---

## 13) Test Plan for Edge Cases

### Automated Tests
- Unit tests: validators, fallback logic, ranking guards.
- Integration tests: `POST /recommendations` with bad/partial/extreme inputs.
- Contract tests: strict response schema validation.
- Load tests: latency and error rate under concurrent traffic.

### Manual QA Scenarios
- Mobile, desktop, and tablet end-to-end flows.
- Slow network and offline simulation.
- Accessibility pass (keyboard-only + screen reader smoke tests).
- No-result and fallback-result UX verification.

### Release Gates
- No critical security issues.
- p95 latency under agreed threshold.
- No unhandled exception in core recommendation flow.
- Accessibility and responsive checks passed.

---

## 14) Definition of Done (Edge-Case Resilience)

The app is edge-case ready when:
- Core recommendation journey remains functional under failure scenarios.
- Users always receive either high-quality recommendations or a graceful fallback.
- The app is usable on mobile, desktop, and tablet for mainstream browsers.
- Critical metrics and alerts are in place to detect regressions early.
