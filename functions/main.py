import firebase_admin
from firebase_functions import scheduler_fn

from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
import requests
import resend

from html_service import get_html_from_events
from scraping_service import get_upcoming_events

firebase_admin.initialize_app()


@scheduler_fn.on_schedule(schedule="* 9 * * 0")
def send_concerts():
    resend.api_key = os.environ.get("RESEND_API_KEY")
    html = get_html_from_events(get_upcoming_events())
    resend.Emails.send(
        {
            "from": "shows4matt@resend.dev",
            "to": os.environ.get("RECIPIENT"),
            "subject": "Tryna see something?",
            "html": html,
        }
    )
