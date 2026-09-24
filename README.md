# PDF Report Generator

Query data with SQL, render it into a PDF report, and serve it by link.

## What It Does

1. **Seed** — Creates a SQLite database with 200 sample orders
2. **Query** — Runs SQL aggregation (COUNT, SUM, GROUP BY)
3. **Render** — Converts data to HTML → PDF using Playwright
4. **Serve** — Generates PDF via API and serves it by link
5. **Idempotent** — Duplicate requests produce one PDF

## How to Run

### 1. Clone and Install

```bash
git clone https://github.com/FurqanArshad0/pdf-report-generator.git
cd pdf-report-generator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium