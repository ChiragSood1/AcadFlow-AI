# AI Academic Workflow Engine (Backend)

Production-grade FastAPI backend for ingesting academic data (attendance CSVs, marks CSVs, academic PDFs) and producing structured, actionable JSON insights for university administrators and faculty.

This system is **not** a chatbot. It exposes a JSON-only API suitable for frontend and integration use.

## High-Level Features

- **Data Ingestion**
  - Upload attendance CSVs
  - Upload marks CSVs
  - Upload academic PDFs
  - Schema validation with clear error reporting

- **Data Normalization**
  - Standardized student identifiers
  - Subject name/code normalization
  - Handling of missing/partial data with explicit strategies

- **Rule-Based Academic Risk Engine**
  - Attendance percentage calculation per subject
  - Combination of attendance + marks
  - Configurable thresholds for Low / Medium / High risk
  - Purely deterministic, testable logic (no AI in calculations)

- **AI Reasoning Layer**
  - Used **only** for explanation, summarization, and recommendations
  - Never performs numeric calculations
  - Produces strictly validated JSON responses

- **Query Routing**
  - Natural language queries from admins/faculty
  - Intent classification into:
    - `intervention_analysis`
    - `attendance_summary`
    - `performance_trends`
  - Routing to appropriate backend logic

## Tech Stack

- **Framework**: FastAPI
- **Data Processing**: pandas
- **Config**: `pydantic-settings`, environment variables
- **Runtime Server**: Uvicorn

## Project Structure (Core)

- `app/main.py` – FastAPI application entrypoint and router registration
- `app/core/config.py` – Application settings, thresholds, and AI configuration
- `app/core/logging.py` – Logging configuration helper
- `app/api/deps.py` – Shared dependencies (e.g., access to in-memory data store)
- `app/api/routes/upload.py` – `/upload/attendance`, `/upload/marks`, `/upload/pdf`
- `app/api/routes/analyze.py` – `/analyze/intervention`, `/analyze/trends`
- `app/api/routes/query.py` – `/query` natural-language router
- `app/models/schemas.py` – Pydantic models for requests/responses
- `app/services/ingestion.py` – CSV/PDF ingestion and schema validation
- `app/services/normalization.py` – ID/subject normalization and missing data handling
- `app/services/risk_engine.py` – Rule-based risk computation
- `app/services/ai_reasoning.py` – AI reasoning adapter for summaries/recommendations
- `app/services/query_router.py` – Intent classification for queries
- `app/utils/pdf_parser.py` – PDF text extraction utilities
- `app/data/store.py` – In-memory data store (placeholder for real persistence)

> TODO: Replace the in-memory store with a real database (e.g., Postgres) and add migrations.

## Running the Backend

### Quick Start

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional for AI features):**
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

4. **Run the API server:**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`.

### API Documentation

Once running, explore the API at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Sample Datasets

To test the API, you need three types of data files:

### 1. Attendance CSV

**Required columns:** `student_id`, `subject`, `date`, `status`

Example: `attendance.csv`
```csv
student_id,subject,date,status
STU001,Mathematics,2025-01-15,Present
STU001,Mathematics,2025-01-16,Present
STU001,Mathematics,2025-01-17,Absent
STU001,Mathematics,2025-01-18,Present
STU001,Physics,2025-01-15,Present
STU001,Physics,2025-01-16,Absent
STU002,Mathematics,2025-01-15,Present
STU002,Mathematics,2025-01-16,Present
STU002,Mathematics,2025-01-17,Present
STU002,Physics,2025-01-15,Absent
STU002,Physics,2025-01-16,Absent
STU003,Mathematics,2025-01-15,Absent
STU003,Mathematics,2025-01-16,Absent
STU003,Mathematics,2025-01-17,Absent
STU003,Physics,2025-01-15,Absent
```

### 2. Marks CSV

**Required columns:** `student_id`, `subject`, `assessment`, `marks_obtained`, `marks_total`

Example: `marks.csv`
```csv
student_id,subject,assessment,marks_obtained,marks_total
STU001,Mathematics,Midterm,85,100
STU001,Mathematics,Final,92,100
STU001,Physics,Midterm,78,100
STU001,Physics,Final,88,100
STU002,Mathematics,Midterm,95,100
STU002,Mathematics,Final,98,100
STU002,Physics,Midterm,89,100
STU002,Physics,Final,91,100
STU003,Mathematics,Midterm,45,100
STU003,Mathematics,Final,52,100
STU003,Physics,Midterm,38,100
STU003,Physics,Final,42,100
```

### 3. Academic PDF

Any PDF file containing academic documents (syllabi, regulations, course descriptions, etc.). The system will extract text for context.

Example: You can use any PDF file (e.g., a course syllabus, academic handbook, etc.)

## Testing the API

### Option 1: Using Swagger UI (Recommended)

1. Navigate to `http://localhost:8000/docs`
2. Click on the `/upload` endpoints
3. Upload your CSV files and PDF
4. Use the `/analyze` and `/query` endpoints to interact with the data

### Option 2: Using cURL

```bash
# Upload attendance CSV
curl -X POST "http://localhost:8000/upload/attendance" \
  -F "file=@attendance.csv"

# Upload marks CSV
curl -X POST "http://localhost:8000/upload/marks" \
  -F "file=@marks.csv"

# Upload PDF
curl -X POST "http://localhost:8000/upload/pdf" \
  -F "file=@academic_handbook.pdf"

# Analyze interventions (identify at-risk students)
curl -X POST "http://localhost:8000/analyze/intervention" \
  -H "Content-Type: application/json" \
  -d '{}'

# Analyze trends
curl -X POST "http://localhost:8000/analyze/trends" \
  -H "Content-Type: application/json" \
  -d '{"group_by_subject": true, "bucket": "W"}'

# Query with natural language
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which students have low attendance in Mathematics?"}'
```

### Option 3: Using Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Upload attendance
with open("attendance.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/upload/attendance", files=files)
    print("Attendance upload:", response.json())

# Upload marks
with open("marks.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/upload/marks", files=files)
    print("Marks upload:", response.json())

# Analyze interventions
response = requests.post(
    f"{BASE_URL}/analyze/intervention",
    json={
        "include_bands": ["high", "medium"]
    }
)
print("Intervention analysis:", response.json())
```

## AI Usage

- The AI layer is **strictly separated** from core numeric logic.
- Risk scores, attendance percentages, and similar metrics are calculated in pure Python/pandas.
- The AI layer receives already-computed metrics and returns:
  - Intervention recommendations
  - Attendance trend summaries
  - Explanatory text for faculty/administrators

> TODO: Plug in a concrete LLM provider (OpenAI, Anthropic, etc.) and harden prompt templates.

## Non-Goals

- This backend is **not** a chat system.
- It does not maintain long-lived conversational state.
- All endpoints are JSON-in / JSON-out and designed to be frontend-ready.

