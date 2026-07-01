# Employment Analytics App

![CI](https://github.com/catalinatan/employment-analytics-app/actions/workflows/python-app.yml/badge.svg?branch=main)
![Python](https://img.shields.io/badge/python-3.10-blue)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)
![Deployed on Render](https://img.shields.io/badge/deployed-Render-46E3B7)

> **Live demo:** [employment-analytics-app.onrender.com](https://employment-analytics-app.onrender.com)

> **Prediction API key caveat:** Gemini usage is quota-limited on the demo. If prediction requests are unavailable due to limits, run the app locally with your own `GENAI_API_KEY`.

---

## What This Project Does

A full-stack data analytics platform for exploring, managing, and forecasting UK regional employment trends — built as a production-grade Flask application with an embedded Dash dashboard and AI-powered prediction.

**Core capabilities:**

- **Interactive data table** — full CRUD on employment records (add, edit, delete, bulk import/export as CSV or XLSX) backed by a relational database
- **Dash analytics dashboard** — embedded at `/dashboard/` using Plotly Dash inside the Flask application context; filters by region, year, gender, and occupation type
- **AI-powered trend forecasting** — calls Gemini 2.0 Flash with Google Search grounding to predict employment percentages N years forward, with error-aware forecasting and structured JSON output parsing
- **Policy workflow** — password-protected routes for submitting policy recommendations and collecting rated feedback, with a one-to-many relational model
- **CI pipeline** — GitHub Actions runs flake8 linting and a 9-file pytest suite (including Selenium UI tests) on every push

---

## Architecture

```mermaid
flowchart TD
    subgraph Client
        Browser
    end

    subgraph Flask Application ["Flask Application (employment_flask_app)"]
        direction TB
        Routes["routes.py\n/  /datatable  /policy_*\n/predict_employment_trends"]
        DashMount["Dash App\nmounted at /dashboard/"]
        RouteHelpers["route_functions.py\nCRUD · AI prediction · Auth decorator"]
    end

    subgraph Data Layer
        SQLite[("SQLite DB\nEmploymentData\nPolicyRecommendation\nPolicyFeedback")]
        ExcelSeed["employment_prepared.xlsx\n(seed data)"]
    end

    subgraph External Services
        Gemini["Gemini 2.0 Flash\n+ Google Search Tool"]
    end

    subgraph CI ["GitHub Actions CI"]
        Lint["flake8 lint"]
        Tests["pytest (9 test files)\nincl. Selenium UI tests"]
    end

    Browser -->|HTTP| Routes
    Browser -->|HTTP| DashMount
    Routes --> RouteHelpers
    RouteHelpers -->|SQLAlchemy ORM| SQLite
    ExcelSeed -->|seed on startup| SQLite
    DashMount -->|reads| SQLite
    RouteHelpers -->|Google GenAI SDK| Gemini
    Gemini -->|structured JSON response| RouteHelpers

    Routes -->|Plotly to_html| Browser
    DashMount -->|Plotly Dash callbacks| Browser

    CI --> Lint
    CI --> Tests
```

---

## Key Engineering Highlights

| Area | Detail |
|---|---|
| **Dash-in-Flask integration** | Dash is initialised inside the Flask app context (`init_dash_app`) and mounted at a sub-path, sharing the SQLAlchemy engine — a non-trivial integration that avoids running two separate servers |
| **AI forecasting pipeline** | Gemini 2.0 Flash is prompted with structured historical data and instructed to return a JSON array; the response is parsed with regex + `json.loads`, converted to a DataFrame, and rendered as an interactive Plotly bar chart |
| **REST-style CRUD API** | The datatable exposes `POST /datatable/add`, `PATCH /datatable/edit`, and `POST /datatable/delete` endpoints consumed by vanilla JS — no frontend framework dependency |
| **Decorator-based auth** | `@password_protected` is a reusable Flask route decorator using `functools.wraps` and `session` storage, applied to policy routes without touching route logic |
| **Import / export** | Users can upload `.xlsx` or `.csv` files to bulk-replace the dataset; export streams the full table via `BytesIO` without writing to disk |
| **ORM constraint design** | `UniqueConstraint` on composite keys prevents duplicate employment records at the database level, with rollback handling surfaced as flash messages |
| **Test coverage** | 9 pytest files covering home page rendering, full CRUD paths, import/export, AI prediction, and policy workflows; Selenium tests cover browser-level interactions |
| **CI on GitHub Actions** | flake8 (syntax errors + complexity checks) and pytest run automatically on every push and pull request |

---

## Screenshots
>
> 1. **Dashboard (`/dashboard/`)**
![Dashboard](docs/screenshots/dashboard.png)

> 3. **Data Table (`/datatable`)** 
![Data Table](docs/screenshots/datatable.png)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3, Blueprints |
| Dashboard | Plotly Dash (embedded in Flask) |
| ORM / DB | SQLAlchemy 2, SQLite |
| AI | Google Gemini 2.0 Flash via `google-genai` SDK |
| Data processing | pandas, openpyxl |
| Visualisation | Plotly Express |
| Forms | Flask-WTF |
| Testing | pytest, Selenium |
| CI | GitHub Actions (flake8 + pytest) |
| Deployment | Render |

---

## Project Structure

```text
.
├── src/
│   └── employment_flask_app/
│       ├── __init__.py            # App factory, SQLAlchemy init, Dash mount
│       ├── routes.py              # All URL routes and request handlers
│       ├── route_functions.py     # CRUD helpers, AI prediction, auth decorator
│       ├── models.py              # ORM models: EmploymentData, PolicyRecommendation, PolicyFeedback
│       ├── db.py                  # Database utilities
│       ├── forms/                 # Flask-WTF form definitions
│       ├── dash_app/              # Dash layout, callbacks, chart builders
│       │   ├── init_dash_app.py
│       │   ├── layout.py
│       │   ├── callbacks.py
│       │   └── charts.py
│       ├── data/
│       │   └── employment_prepared.xlsx   # Seed dataset
│       └── templates/             # Jinja2 HTML templates
├── tests/                         # 9-file pytest suite (unit + Selenium UI)
│   ├── conftest.py
│   ├── test_home_page.py
│   ├── test_datatable.py
│   ├── test_add_row.py
│   ├── test_edit_cell.py
│   ├── test_delete_row.py
│   ├── test_import_export.py
│   ├── test_predict_trend.py
│   ├── test_pol_feedback.py
│   └── test_rec_policy.py
├── .github/workflows/python-app.yml
├── pyproject.toml
└── requirements.txt
```

---

## Local Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/catalina-angelia/employment-analytics-app.git
cd employment-analytics-app

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -e .
pip install -r requirements.txt

# 4. Set environment variables
export SECRET_KEY=your-secret-key
export GENAI_API_KEY=your-google-genai-key         # Required for AI prediction
export ENTERPRISE_API_KEY=$(python -c 'import secrets;print(secrets.token_urlsafe(32))')
                                                    # Required for /api/v1 endpoints

# 5. Run the app
flask --app employment_flask_app run --debug
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000). The dashboard is at `/dashboard/`.

---

## Enterprise JSON API (`/api/v1`)

A headless JSON surface used by Power Automate flows and Copilot Studio agents. Every non-`/health` endpoint requires an `x-api-key` header matching `ENTERPRISE_API_KEY`.

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/api/v1/health` | Warm-ping (unauthenticated). |
| `POST` | `/api/v1/trigger-forecast` | Run Gemini forecast, persist it, return summary + anomaly count. |
| `GET`  | `/api/v1/latest-forecast?region=&occupation_type=` | Return most recent persisted forecast. |
| `GET`  | `/api/v1/anomalies?region=` | Return z-score outliers (|z|>2.5) in local data. |

Example:

```bash
curl -X POST https://employment-analytics-app.onrender.com/api/v1/trigger-forecast \
  -H "x-api-key: $ENTERPRISE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"region":"England","occupation_type":"2: professional occupations","no_of_years":3}'
```

Errors surface as structured JSON (`400` bad request, `401` unauthorized, `404` not found, `429` upstream quota, `502` upstream failed) instead of HTML — designed for low-code parsers.

---

## Running Tests

```bash
pytest
```

The suite covers CRUD operations, home page rendering, file import/export, AI trend prediction, and policy management — including browser-level Selenium tests.

---

## Deployment

The app is deployed on **Render** at [employment-analytics-app.onrender.com](https://employment-analytics-app.onrender.com).

> **Note:** Render free-tier instances spin down after inactivity. If the page takes ~30 seconds to load on first visit, it is waking up — subsequent requests are fast.

---

## Data Attribution

Employment data sourced from the [Annual Population Survey (APS)](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/methodologies/annualpopulationsurveyapsqmi) published by the UK Office for National Statistics (ONS), licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
