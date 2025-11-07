# backend/tasks.py

from datetime import datetime
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64, os, io, csv, traceback
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from backend.celery_app import celery

# Lazy imports inside tasks to avoid circular import issues
from backend.models.db_setup import db

load_dotenv()


# ------------------------------------------------------------
# ✉️ Helper function for sending email via SendGrid
# ------------------------------------------------------------
def send_email(to_email, subject, html_content, attachment_bytes=None, attachment_name=None, mime_type=None):
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        message = Mail(
            from_email="23f3001911@ds.study.iitm.ac.in",
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        # Optional attachment support
        if attachment_bytes and attachment_name:
            encoded_file = base64.b64encode(attachment_bytes).decode()
            attachment = Attachment(
                FileContent(encoded_file),
                FileName(attachment_name),
                FileType(mime_type or "application/octet-stream"),
                Disposition("attachment")
            )
            message.attachment = attachment

        sg.send(message)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        traceback.print_exc()


# ------------------------------------------------------------
# 🕒 Simple reminder and scheduled tasks
# ------------------------------------------------------------
@celery.task
def send_reminder_email(to_email, subject, message):
    html_content = f"<p>{message}</p>"
    send_email(to_email, subject, html_content)
    return f"Email sent to {to_email}"


@celery.task
def send_daily_reminder(to_email, name):
    message = f"Hello {name}, this is your automated reminder from the Flask + Celery system!"
    send_email(to_email, "Daily Reminder", f"<p>{message}</p>")
    print(f"✅ Daily reminder sent to {to_email}")
    return f"Daily reminder sent to {to_email}"


# ------------------------------------------------------------
# 📅 Monthly report task
# ------------------------------------------------------------
@celery.task
def send_monthly_report_task(user_email, user_name):
    from backend.reports.report_generator import generate_monthly_report

    user_data = {
        "name": user_name,
        "email": user_email,
        "projects": 5,
        "tasks_completed": 12,
        "meetings": 4
    }

    pdf_bytes = generate_monthly_report(user_data)

    send_email(
        user_email,
        "Your Monthly Activity Report",
        f"<p>Dear {user_name},</p><p>Here is your monthly report summary!</p>",
        attachment_bytes=pdf_bytes,
        attachment_name="Monthly_Report.pdf",
        mime_type="application/pdf"
    )
    print(f"✅ Monthly report sent to {user_email}")


# ------------------------------------------------------------
# 📤 Export Parking/Reservation History to CSV
# ------------------------------------------------------------
@celery.task
def export_parking_history_task(admin_email):
    """
    Generate CSV of reservation history and email it asynchronously.
    """
    from backend.app import create_app
    from backend.models.Reservation import Reservation
    from backend.models.User import User
    from backend.models.ParkingSpot import ParkingSpot
    from backend.models.ParkingLot import ParkingLot

    app = create_app()

    with app.app_context():
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "Reservation ID", "User", "Location", "Spot ID",
                "Parking Time", "Leaving Time", "Parking Cost (₹)"
            ])
            print("hello debugging ")
            reservations = Reservation.query.all()
            print(f"ℹ️ Found {len(reservations)} reservations to export.")
            for r in reservations:
                user = User.query.get(r.user_id)
                spot = ParkingSpot.query.get(r.spot_id)
                lot = ParkingLot.query.get(spot.lot_id) if spot else None

                writer.writerow([
                    r.id,
                    user.username if user else "N/A",
                    lot.prime_location_name if lot else "N/A",
                    r.spot_id,
                    r.parking_timestamp or "",
                    r.leaving_timestamp or "",
                    r.parking_cost
                ])

            csv_bytes = output.getvalue().encode()

            send_email(
                admin_email,
                "Reservation History CSV Export",
                "<p>Dear Admin,</p><p>Your parking reservation history export is ready.</p>",
                attachment_bytes=csv_bytes,
                attachment_name="Reservation_History.csv",
                mime_type="text/csv"
            )

            print(f"✅ Export task completed successfully for {admin_email}")
            return f"Export completed for {admin_email}"

        except Exception as e:
            traceback.print_exc()
            print(f"❌ Export task failed for {admin_email}: {e}")
            raise



#celery -A backend.celery_app.celery worker --loglevel=info --pool=solo --concurrency=1