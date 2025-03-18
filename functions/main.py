# The Cloud Functions for Firebase SDK to set up triggers and logging.
from firebase_functions import scheduler_fn

# The Firebase Admin SDK to delete users.
import firebase_admin
from firebase_admin import auth

from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup

import resend

firebase_admin.initialize_app()

HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

@dataclass
class Event:
  date: object
  img: str
  link: str
  price: str
  source: str
  title: str

  def to_html(self):
    return f'<div style="margin:auto;"><h3><a href="{self.link}">{self.title}</a></h3>' + \
           f'<img style="max-width: 400px;" src="{self.img}">' + \
           f'<p style="color: brown;">{self.date.strftime("%a %m/%d")}</p>' + \
           f'<p style="color: brown;">{self.price}</p>' + \
           f'<p style="color: brown;">source: {self.source}</p></div>'

def get_soup_from_url(url):
  resp = requests.get(url, headers = HEADERS)
  return BeautifulSoup(resp.content, 'html.parser')

def get_anthem_events():
  soup = get_soup_from_url('https://theanthemdc.com/calendar/')
  event_elements = soup.find_all('div', class_='event')

  events = []
  for event_element in event_elements:
    date_string = event_element.find('div', class_='event__date').text.strip()
    date = datetime.strptime(date_string + "/2025", '%m/%d/%Y')
    link = event_element.find('div', class_='event__content').find("a")['href']
    img = event_element.find('img')["data-src"]
    price = event_element.find('div', class_='event__tickets').find("p").text.strip()
    title = event_element.find('div', class_='event__content').find("h3").text.strip()
    events.append(Event(date, img,link, price, "Anthem", title))

  return events

def get_930_events():
  soup = get_soup_from_url('https://www.930.com/')
  event_elements = soup.find_all('article', class_='list-view-item card event-status-live')[2:]

  events = []
  for event_element in event_elements:
    date_string = " ".join(event_element.find('span', class_='dates').text.strip().split()[1:])
    date = datetime.strptime(date_string + " 2025", "%d %b %Y")
    title_element = event_element.find("h3", class_="h1 event-name headliners")
    link = title_element.find("a")["href"]
    img = event_element.find("img")["data-src"]
    price = " ".join(event_element.find('section', class_='ticket-price external-ticket').text.strip().split())
    title = title_element.text.strip()
    events.append(Event(date, img,link, price, "930", title))
  return events

def get_blackcat_events():
  soup = get_soup_from_url('https://www.blackcatdc.com/schedule.html')
  event_elements = soup.find_all('div', class_='show')[:-1]

  events = []
  for event_element in event_elements:
    date_string = event_element.find('h2', class_='date').text.strip()
    date = datetime.strptime(date_string + " 2025", "%A %B %d %Y")
    link = event_element.find("a")["href"]
    img = "https://www.blackcatdc.com" + event_element.find("img")["src"]
    price = event_element.find('p', class_='show-text').text.strip()
    title = event_element.find("h1", class_="headline").text.strip()
    events.append(Event(date, img,link, price, "black cat", title))
  return events

def get_html_from_events(events):
  events.sort(key=lambda event: event.date)
  html = '<div style="background-color:powderblue;">' + \
        '<table width="100%" border="0" cellspacing="0" cellpadding="0">' + \
        '<tr><td align="center">' + \
        '<h1 style="color: brown;">woah look at these shows</h1>' + \
        '<hr style="border:none;background-color:purple;height:2px;width:80%;"/>'
  for event in events:
    html += event.to_html()
    html += '<hr style="border:none;background-color:purple;height:1px;width:80%;"/>'
  html += "</td></tr></table></div>"
  return html

@scheduler_fn.on_schedule(schedule="* 9 * * 0")
def send_concerts():
    resend.api_key = os.environ.get("RESEND_API_KEY")
    html = get_html_from_events(get_blackcat_events() + get_930_events() + get_anthem_events())
    resend.Emails.send({
        "from": "shows4matt@resend.dev",
        "to": "matthewparulski@gmail.com",
        "subject": "Hello World",
        "html": html
    })