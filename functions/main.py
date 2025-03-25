import firebase_admin
from firebase_functions import scheduler_fn

import os
import resend

from html_service import get_html_from_events
from scraping_service import get_upcoming_events

firebase_admin.initialize_app()


@scheduler_fn.on_schedule(schedule="1 9 * * 0", secrets=["RESEND_API_KEY", "RECIPIENT"])
def send_concerts(event):
    resend.api_key = os.environ.get("RESEND_API_KEY")
    html = get_html_from_events(get_upcoming_events())
    resend.Emails.send(
        {
            "cc": "afpiliero@gmail.com",
            "from": "shows4matt@definitelya.website",
            "html": html,
            "subject": "Tryna see something?",
            "to": os.environ.get("RECIPIENT"),
        }
    )
