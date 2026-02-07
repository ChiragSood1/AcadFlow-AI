# AcadFlow AI — Academic Workflow Engine (Backend)

A backend-focused academic workflow system built with FastAPI for ingesting institutional academic data and producing structured, actionable insights for faculty and administrators.

**This project is not a chatbot.**
It exposes a JSON-only API designed for frontend integration, dashboards, and administrative tooling.

---

## 🎯 Project Overview

AcadFlow AI ingests academic datasets such as:

- Attendance records (CSV)
- Marks / assessment data (CSV)
- Academic documents (PDF)

It normalizes and analyzes this data using deterministic, rule-based logic, and optionally applies an AI reasoning layer only for explanation and summarization — never for numeric computation.

---

## 🚀 Key Capabilities

### 1. Data Ingestion

- Upload attendance CSV files
- Upload marks CSV files
- Upload academic PDFs
- Schema validation with clear, structured error responses

### 2. Data Normalization

- Standardized student identifiers
- Subject name and code normalization
- Explicit handling of missing or partial data

### 3. Rule-Based Academic Risk Engine

- Attendance percentage calculation per subject
- Combined attendance + marks evaluation
- Configurable thresholds for:
  - Low Risk
  - Medium Risk
  - High Risk
- Fully deterministic and testable logic
- No AI involved in calculations

### 4. AI Reasoning Layer (Optional)

Used only for:

- Explanations
- Summaries
- Intervention recommendations

Never performs numeric calculations. Produces strictly validated JSON output.

### 5. Query Routing

- Accepts natural-language queries from administrators or faculty
- Routes queries to appropriate backend logic using intent classification:
  - `attendance_summary`
  - `performance_trends`
  - `intervention_analysis`

---

## 🧱 Tech Stack

- **Framework**: FastAPI
- **Data Processing**: pandas
- **Configuration**: pydantic-settings, environment variables
- **Server**: Uvicorn

---

## 📁 Project Structure

```
app/
├── main.py                  # FastAPI app entrypoint
├── core/
│   ├── config.py             # Application settings and thresholds
│   └── logging.py            # Logging configuration
├── api/
│   ├── deps.py               # Shared dependencies
│   └── routes/
│       ├── upload.py         # CSV/PDF upload endpoints
│       ├── analyze.py        # Risk analysis endpoints
│       └── query.py          # Natural language query router
├── models/
│   └── schemas.py            # Pydantic request/response models
├── services/
│   ├── ingestion.py          # CSV/PDF ingestion and validation
│   ├── normalization.py      # Data normalization logic
│   ├── risk_engine.py        # Rule-based risk computation
│   ├── ai_reasoning.py       # AI explanation adapter
│   └── query_router.py       # Intent classification
├── utils/
│   └── pdf_parser.py         # PDF text extraction
└── data/
    └── store.py              # In-memory data store
```

> **Note**: The in-memory store is a placeholder.
> Future improvements may include persistent storage (e.g., PostgreSQL).

---

## ▶️ Running the Backend

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure AI features

```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
👉 **http://localhost:8000**

---

## 📘 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 Sample Datasets

### 1. Attendance CSV

**Required columns:**
```
student_id,subject,date,status
```

**Example:**
```csv
STU001,Mathematics,2025-01-15,Present
STU001,Mathematics,2025-01-16,Absent
STU002,Physics,2025-01-15,Present
```

### 2. Marks CSV

**Required columns:**
```
student_id,subject,assessment,marks_obtained,marks_total
```

**Example:**
```csv
STU001,Mathematics,Midterm,85,100
STU001,Mathematics,Final,92,100
```

### 3. Academic PDF

Any academic document such as:
- Syllabus
- Academic handbook
- Course regulations

The system extracts text for contextual analysis.

---

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Upload CSV and PDF files
3. Call /analyze and /query endpoints

### Using cURL

```bash
curl -X POST "http://localhost:8000/upload/attendance" \
  -F "file=@attendance.csv"
```

---

## 🤖 AI Usage Philosophy

- **AI is never used for calculations**
- All metrics are computed via Python/pandas
- AI receives pre-computed data and returns:
  - Summaries
  - Explanations
  - Recommendations

This ensures:
- ✅ Transparency
- ✅ Testability
- ✅ Deterministic academic evaluation

---

## ❌ Non-Goals

- Not a chat system
- No long-lived conversational memory
- No frontend UI
- No AI-driven grading or scoring

---

## 🛠️ Future Improvements

- Replace in-memory store with a database
- Add migrations and persistence
- Harden AI prompt templates
- Extend analytics endpoints

---

## 📌 Project Status

This project is a backend-focused academic workflow prototype intended for learning, experimentation, and portfolio demonstration.
    