# reports/report_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_monthly_report(user_data):
    """
    Generates a PDF report for a given user and returns it as bytes.
    user_data: dict containing user's info and stats
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 800, f"Monthly Activity Report - {user_data['name']}")

    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Email: {user_data['email']}")
    c.drawString(100, 750, f"Total Projects: {user_data['projects']}")
    c.drawString(100, 730, f"Tasks Completed: {user_data['tasks_completed']}")
    c.drawString(100, 710, f"Meetings Attended: {user_data['meetings']}")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 680, "Generated automatically by Industry Academia Portal")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
