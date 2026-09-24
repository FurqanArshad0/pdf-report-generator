import os
from datetime import datetime
from playwright.async_api import async_playwright
from src.db import get_db

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def get_report_data():
    """Run SQL aggregation queries and return a report object."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    # Total revenue
    cursor.execute("SELECT SUM(amount) FROM orders")
    total_revenue = round(cursor.fetchone()[0] or 0, 2)
    
    # Top 5 products by revenue
    cursor.execute("""
        SELECT product, SUM(amount) as revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
    """)
    top_products = [dict(row) for row in cursor.fetchall()]
    
    # Orders per day (last 7 days)
    cursor.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM orders
        WHERE created_at >= DATE('now', '-7 days')
        GROUP BY day
        ORDER BY day DESC
    """)
    orders_per_day = [dict(row) for row in cursor.fetchall()]
    
    # All orders (for the long table)
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    all_orders = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "top_products": top_products,
        "orders_per_day": orders_per_day,
        "all_orders": all_orders,
        "generated_at": datetime.now().isoformat()
    }

def build_html(data):
    """Build an HTML page from report data."""
    # Build top products table
    top_rows = ""
    for p in data["top_products"]:
        top_rows += f"<tr><td>{p['product']}</td><td>${p['revenue']:.2f}</td></tr>"
    
    # Build daily orders table
    daily_rows = ""
    for d in data["orders_per_day"]:
        daily_rows += f"<tr><td>{d['day']}</td><td>{d['count']}</td></tr>"
    
    # Build all orders table
    all_rows = ""
    for o in data["all_orders"]:
        all_rows += f"""
        <tr>
            <td>{o['id']}</td>
            <td>{o['customer']}</td>
            <td>{o['product']}</td>
            <td>${o['amount']:.2f}</td>
            <td>{o['created_at'][:10]}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Sales Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #1E3A5F; }}
            h2 {{ color: #4A90D9; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #1E3A5F; color: white; }}
            tr {{ break-inside: avoid; }}
            .totals {{ display: flex; gap: 30px; margin: 20px 0; }}
            .total-box {{ background: #f0f4f8; padding: 15px; border-radius: 8px; }}
            .total-box h3 {{ margin: 0; color: #666; font-size: 14px; }}
            .total-box p {{ margin: 5px 0 0; font-size: 24px; font-weight: bold; color: #1E3A5F; }}
        </style>
    </head>
    <body>
        <h1>📊 Sales Report</h1>
        <p>Generated: {data['generated_at'][:19]}</p>
        
        <div class="totals">
            <div class="total-box">
                <h3>Total Orders</h3>
                <p>{data['total_orders']}</p>
            </div>
            <div class="total-box">
                <h3>Total Revenue</h3>
                <p>${data['total_revenue']:.2f}</p>
            </div>
        </div>
        
        <h2>Top 5 Products by Revenue</h2>
        <table>
            <thead>
                <tr><th>Product</th><th>Revenue</th></tr>
            </thead>
            <tbody>
                {top_rows}
            </tbody>
        </table>
        
        <h2>Orders Per Day (Last 7 Days)</h2>
        <table>
            <thead>
                <tr><th>Day</th><th>Orders</th></tr>
            </thead>
            <tbody>
                {daily_rows}
            </tbody>
        </table>
        
        <h2>All Orders</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Customer</th><th>Product</th><th>Amount</th><th>Date</th></tr>
            </thead>
            <tbody>
                {all_rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html

async def render_pdf(html, output_path):
    """Render HTML to PDF using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html)
        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True
        )
        await browser.close()

async def generate_report():
    """Run the full pipeline: query → render → save."""
    data = get_report_data()
    html = build_html(data)
    
    # Get a new report ID
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reports (path, created_at) VALUES (?, ?)", 
                   ("", datetime.now().isoformat()))
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Render PDF
    output_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")
    await render_pdf(html, output_path)
    
    # Update the report path
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE reports SET path = ? WHERE id = ?", (output_path, report_id))
    conn.commit()
    conn.close()
    
    return report_id