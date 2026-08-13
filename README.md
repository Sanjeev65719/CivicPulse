# 🏛️ CivicPulse — Municipal Grievance & Civic Infrastructure Analytics Agent

> **An end-to-end Streamlit application for ingesting civic complaint data, detecting geographic hotspots, predicting SLA breaches, and generating resource-allocation priority reports for municipal staff.**

---

## 🎯 Problem Statement

Urban local bodies across India process **thousands of civic complaints daily** — potholes, garbage, streetlight outages, water leaks, drainage blocks — yet most municipal analytics remain manual, siloed, and reactive. There is no easy way for ward engineers or city administrators to:

- **Detect geographic clusters** of recurring complaints (hotspots)
- **Predict which open complaints** are at risk of breaching their SLA deadlines
- **Query complaint data** using natural language instead of SQL
- **Visualise trends** across wards, categories, and time periods

CivicPulse bridges this gap by combining **data engineering, machine learning, and interactive visualisation** into a single, self-contained tool that works offline with SQLite and requires zero cloud infrastructure.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **UI** | Streamlit | Interactive web dashboard |
| **Data Handling** | pandas, NumPy | Ingestion, cleaning, transformation |
| **Storage** | SQLAlchemy + SQLite | Persistent local database |
| **Hotspot Detection** | scikit-learn (DBSCAN) | Geographic clustering with haversine metric |
| **SLA Prediction** | scikit-learn (Random Forest) | Classification of breach risk |
| **Visualisation** | Plotly, Plotly Express | Charts and interactive maps |
| **Profiling** | ydata-profiling | Automated EDA reports |
| **NLP (optional)** | Hugging Face Inference API | Natural-language-to-SQL translation |

---

## ✨ Features

1. **Data Ingestion** — Upload CSV/XLSX, load built-in sample data, or fetch from REST APIs
2. **Data Cleaning** — Quality assessment, missing-value handling, deduplication, coordinate validation, date parsing with derived resolution-time column
3. **SQLite Storage & Querying** — Save cleaned data, run raw SQL, or ask questions in plain English
4. **Hotspot Detection** — DBSCAN clustering on lat/long (haversine metric), severity-ranked hotspot table, interactive Mapbox map
5. **SLA Breach Prediction** — Random Forest classifier trained on historical resolutions; predicts breach probability for every open complaint; generates priority action recommendations
6. **Visualisation Dashboard** — Category breakdown (pie + bar), ward comparison (colour-coded by resolution time), monthly resolution trend, SLA breach distribution
7. **Profiling Report** — One-click auto-EDA with ydata-profiling (graceful fallback to pandas-based stats)
8. **Settings** — HF API key management, model status, session reset

---

## 📁 Project Structure

```
CivicPulse/
├── app.py                          # Main Streamlit application (8 tabs)
├── modules/
│   ├── __init__.py
│   ├── data_ingestion.py           # CSV/XLSX/API data loading
│   ├── data_cleaning.py            # Quality assessment & cleaning
│   ├── database_manager.py         # SQLAlchemy + SQLite wrapper
│   ├── ai_services.py              # NLP-to-SQL (HF API + rule-based)
│   ├── hotspot_detection.py        # DBSCAN geographic clustering
│   ├── sla_prediction.py           # Random Forest SLA predictor
│   ├── visualization.py            # Plotly chart factory
│   └── profiling.py                # ydata-profiling wrapper
├── utils/
│   ├── __init__.py
│   └── helpers.py                  # Haversine, SLA thresholds, file utils
├── sample_data/
│   └── civic_complaints_sample.csv # 300-row synthetic dataset
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI (app.py)                     │
│  ┌──────┐ ┌──────┐ ┌───────┐ ┌───────┐ ┌─────┐ ┌────┐ ┌────┐  │
│  │Ingest│ │Clean │ │Storage│ │Hotspot│ │ SLA │ │ Viz│ │Prof│  │
│  └──┬───┘ └──┬───┘ └───┬───┘ └───┬───┘ └──┬──┘ └─┬──┘ └─┬──┘  │
└─────┼────────┼─────────┼─────────┼────────┼──────┼──────┼──────┘
      │        │         │         │        │      │      │
      v        v         v         v        v      v      v
┌──────────┐ ┌────────┐ ┌───────┐ ┌──────┐ ┌────┐ ┌────┐ ┌─────┐
│  data_   │ │ data_  │ │  db_  │ │hotsp.│ │sla_│ │viz.│ │prof.│
│ingestion │ │cleaning│ │manager│ │detect│ │pred│ │    │ │     │
└──────────┘ └────────┘ └───┬───┘ └──────┘ └─┬──┘ └────┘ └─────┘
                            │                │
                            v                v
                      ┌──────────┐    ┌────────────┐
                      │  SQLite  │    │   utils/    │
                      │   (.db)  │    │  helpers.py │
                      └──────────┘    └────────────┘
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd CivicPulse

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) Set Hugging Face API key for AI-powered NLP queries
set HF_API_KEY=your_token_here   # Windows
export HF_API_KEY=your_token_here # macOS/Linux

# 6. Launch the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

### Quick Start Workflow

1. Go to **Data Ingestion** → click **Load Sample Data**
2. Go to **Data Cleaning** → run all cleaning steps → click **Finalize Cleaned Data**
3. Go to **Storage & Queries** → **Save DataFrame to SQLite** → try a natural-language query
4. Go to **Hotspot Detection** → **Run Hotspot Detection** → view the map
5. Go to **SLA Prediction** → **Train SLA Prediction Model** → **Predict** breach risk
6. Go to **Visualization** → explore all charts
7. Go to **Profiling Report** → generate the auto-EDA report

---

## 📸 Screenshots

*Screenshots will be added after deployment.*

---

## 📝 Individual Project

**Author:** Meera  
**Project:** CivicPulse — Municipal Grievance & Civic Infrastructure Analytics Agent

---

## 📄 License

This project is for educational and demonstration purposes.
