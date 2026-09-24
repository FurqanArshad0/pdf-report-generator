from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime, date
import os
from src.db import get_db, init_db
from src.report import generate_report

app = FastAPI(title="PDF Report Generator", version="1.0.0")

# Initialize database on startup
init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports", status_code=201)
async def create_report(force: bool = False):
    """Generate a new PDF report."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Idempotency: check if a report was already generated today
    if not force:
        today = date.today().isoformat()
        cursor.execute(
            "SELECT id, path FROM reports WHERE DATE(created_at) = ?",
            (today,)
        )
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return {
                "id": existing["id"],
                "file": f"/reports/{existing['id']}/file",
                "message": "Report already generated today",
                "created_at": existing["path"]
            }
    
    conn.close()
    
    # Generate new report
    report_id = await generate_report()
    
    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file",
        "message": "Report generated"
    }

@app.get("/reports/{report_id}")
def get_report(report_id: int):
    """Get a report record by ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "id": row["id"],
        "path": row["path"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file"
    }

@app.get("/reports/{report_id}/file")
def download_report(report_id: int):
    """Download the PDF file."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not os.path.exists(row["path"]):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(row["path"], media_type="application/pdf", filename=f"report-{report_id}.pdf")