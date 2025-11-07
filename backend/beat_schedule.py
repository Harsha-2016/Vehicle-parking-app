# backend/beat_schedule.py
from celery import Celery
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-daily-reminders': {
        'task': 'tasks.send_daily_reminder',
        'schedule': crontab(hour=10,minute=0),  
        'args': ('23f3001911@ds.study.iitm.ac.in', 'Harsha'),
    },
    "send-monthly-reports": {
        "task": "tasks.send_monthly_report_task",
        "schedule": crontab(day_of_month=1 , hour= 8 , minute=0 ),
        "args": ("23f3001911@ds.study.iitm.ac.in", "John Doe")
    }
}

#celery -A tasks.celery beat --loglevel=info