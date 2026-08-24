# Farmer Friendly — Regenerative Agriculture Network

Built for **Build with AI: Code for Communities** —
**AgriN & Regenerative Agricultural Intelligence** track.

## The problem

Small and marginal farmers across India lack access to data-driven
agricultural guidance. Relying on traditional methods instead of
satellite data, soil health analytics, and climate forecasting leads to
crop failure and threatens food security. The absence of shared digital
infrastructure also blocks cross-state collaboration on climate-resilient
farming.

## What this does

Farmer Friendly is an interoperable digital agriculture network with
three connected parts:

1. **Diagnose Crop** — a farmer uploads a photo of their crop or leaf.
   Gemini Vision identifies visible disease, pest damage, or nutrient
   issues, and recommends regenerative (low-cost, sustainable) care
   steps.
2. **Get Recommendation** — a farmer selects their state, soil type, and
   season. Gemini recommends climate-resilient crops and regenerative
   practices grounded in that region's soil and climate profile.
3. **State Cooperation Dashboard** — every diagnosis and recommendation
   is aggregated by state, so patterns (common crop issues, regional
   recommendation trends) are visible across state lines — the "digital
   public good enabling states to share agricultural data models"
   requirement.

## How it satisfies the challenge

- **AI-driven agro-advisories**: Gemini powers both the diagnostic tool
  and the regenerative crop recommendation engine — the two required
  capabilities in the brief.
- **Regenerative recommendations based on soil, season, and regional
  context**: each recommendation is grounded in a representative
  soil/climate profile per state (see honest scope note below).
- **Diagnostic tool for crop diseases**: image-based diagnosis via
  Gemini Vision.
- **Scalable digital public good, cross-state cooperation**: the State
  Cooperation Dashboard aggregates data across all participating states
  into a shared view — any state can see what issues and
  recommendations are trending elsewhere, supporting coordinated
  climate-resilient planning rather than each state working in
  isolation.

## Tech stack

- **Frontend**: HTML/CSS/JS
- **Backend**: Flask + SQLite
- **AI**: Gemini 1.5 Flash (Vision for diagnosis, text for recommendations)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your Gemini API key:
   ```
   GOOGLE_API_KEY=your_key_here
   ```
3. Run the backend:
   ```bash
   python server.py
   ```
4. Open `project.html` in your browser. It's wired to `http://localhost:5000`.

## Testing it

1. **Diagnose Crop**: pick a state, upload any plant/leaf photo, click
   Diagnose Crop.
2. **Get Recommendation**: pick a state, soil type, and season, click
   Get Recommendation.
3. **State Dashboard**: switch tabs — see both submissions aggregated,
   with common-issue and per-state breakdowns.

## Honest scope notes (for the pitch deck / judges)

Built within a hackathon timeframe — these are the deliberate scoping
decisions and what a production version would add:

- **Satellite data, live soil health sensors, and real-time weather
  forecasting are not yet integrated.** The current version uses a
  representative soil/climate context table per state to ground the AI's
  reasoning realistically. Production version would integrate Google
  Earth Engine (satellite imagery), India's Soil Health Card data, and
  IMD weather forecasts, as outlined in the hackathon's own suggested
  tech stack.
- **Cross-state data sharing is implemented as a shared aggregated
  dashboard**, not yet a formal inter-state data exchange protocol.
  This demonstrates the core "shared visibility" concept; a production
  version would define proper data governance and API contracts between
  state agricultural departments.
- **Multilingual/voice support is not yet built into this specific
  flow** — a natural next addition using Cloud Speech-to-Text and
  Translation API, following the same approach used elsewhere in this
  hackathon submission process.

## Cross-border applicability (BRICS scalability)

While this prototype is scoped to India's states, the underlying
architecture is not India-specific in its logic. The core mechanism —
(1) a regional context table describing soil/climate/farming
conditions, (2) Gemini reasoning grounded in that context, (3) an
aggregated cross-region dashboard — generalizes directly to other
BRICS nations:

- **Brazil**: swap the state context table for Brazil's states
  (e.g. Mato Grosso, Paraná), covering tropical/subtropical soy,
  coffee, and maize agriculture.
- **Russia**: swap for Russian federal subjects, covering continental
  climate wheat and sunflower agriculture.
- **South Africa**: swap for South African provinces, covering
  semi-arid maize and citrus farming.
- **China**: swap for Chinese provinces, covering intensive
  smallholder rice and vegetable agriculture.

No change to the Gemini prompts, the diagnosis flow, or the dashboard
aggregation logic is required — only the regional context data source
changes per country. This is the same "one model, many regions" design
principle used throughout this prototype, making it realistically
deployable as shared infrastructure across BRICS nations rather than
requiring a separate rebuild per country.
