from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    date: object
    img: str
    link: str
    price: str
    source: str
    title: str

    def to_html(self):
        return (
            f'<div style="margin:auto;"><h3><a href="{self.link}">{self.title}</a></h3>'
            + f'<img style="max-width: 400px;" src="{self.img}">'
            + f'<p style="color: brown;">{self.date.strftime("%a %m/%d")}</p>'
            + f'<p style="color: brown;">{self.price}</p>'
            + f'<p style="color: brown;">source: {self.source}</p></div>'
        )


class BaseScraper:
    _HEADERS = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }
    _SOURCE = ""
    _URL = ""

    @staticmethod
    def _set_year_on_date(date):
        if date.replace(year=datetime.now().year) > datetime.now():
            return date.replace(year=datetime.now().year)
        else:
            return date.replace(year=datetime.now().year + 1)

    @classmethod
    def _get_date_from_event_element(cls, event_element):
        pass

    @classmethod
    def _get_event_elements(cls):
        pass

    @classmethod
    def _get_img_from_event_element(cls, event_element):
        pass

    @classmethod
    def _get_link_from_event_element(cls, event_element):
        pass

    @classmethod
    def _get_price_from_event_element(cls, event_element):
        pass

    @classmethod
    def _get_soup_from_url(cls):
        resp = requests.get(cls._URL, headers=cls._HEADERS)
        return BeautifulSoup(resp.content, "html.parser")

    @classmethod
    def _get_title_from_event_element(cls, event_element):
        pass

    @classmethod
    def get_events(cls):
        event_elements = cls._get_event_elements()
        events = []
        for event_element in event_elements:
            events.append(
                Event(
                    cls._get_date_from_event_element(event_element),
                    cls._get_img_from_event_element(event_element),
                    cls._get_link_from_event_element(event_element),
                    cls._get_price_from_event_element(event_element),
                    cls._SOURCE,
                    cls._get_title_from_event_element(event_element),
                )
            )
        return events


class AnthemScraper(BaseScraper):
    _SOURCE = "Anthem"
    _URL = "https://theanthemdc.com/calendar/"

    @classmethod
    def _get_date_from_event_element(cls, event_element):
        date_string = event_element.find("div", class_="event__date").text.strip()
        return cls._set_year_on_date(datetime.strptime(date_string, "%m/%d"))

    @classmethod
    def _get_event_elements(cls):
        soup = cls._get_soup_from_url()
        return soup.find_all("div", class_="event")

    @classmethod
    def _get_img_from_event_element(cls, event_element):
        return event_element.find("img")["data-src"]

    @classmethod
    def _get_link_from_event_element(cls, event_element):
        return event_element.find("div", class_="event__content").find("a")["href"]

    @classmethod
    def _get_price_from_event_element(cls, event_element):
        return event_element.find("div", class_="event__tickets").find("p").text.strip()

    @classmethod
    def _get_title_from_event_element(cls, event_element):
        return (
            event_element.find("div", class_="event__content").find("h3").text.strip()
        )


class NineThirtyScraper(BaseScraper):
    _SOURCE = "930"
    _URL = "https://www.930.com/"

    @classmethod
    def _get_date_from_event_element(cls, event_element):
        date_string = " ".join(
            event_element.find("span", class_="dates").text.strip().split()[1:]
        )
        return cls._set_year_on_date(datetime.strptime(date_string, "%d %b"))

    @classmethod
    def _get_event_elements(cls):
        soup = cls._get_soup_from_url()
        return soup.find_all("article", class_="list-view-item card event-status-live")[
            2:
        ]

    @classmethod
    def _get_img_from_event_element(cls, event_element):
        return event_element.find("img")["data-src"]

    @classmethod
    def _get_link_from_event_element(cls, event_element):
        return event_element.find("h3", class_="h1 event-name headliners").find("a")[
            "href"
        ]

    @classmethod
    def _get_price_from_event_element(cls, event_element):
        return " ".join(
            event_element.find("section", class_="ticket-price external-ticket")
            .text.strip()
            .split()
        )

    @classmethod
    def _get_title_from_event_element(cls, event_element):
        return event_element.find("h3", class_="h1 event-name headliners").text.strip()


class BlackCatScraper(BaseScraper):
    _SOURCE = "Black Cat"
    _URL = "https://www.blackcatdc.com/schedule.html"

    @classmethod
    def _get_date_from_event_element(cls, event_element):
        date_string = event_element.find("h2", class_="date").text.strip()
        return cls._set_year_on_date(datetime.strptime(date_string, "%A %B %d"))

    @classmethod
    def _get_event_elements(cls):
        soup = cls._get_soup_from_url()
        return soup.find_all("div", class_="show")[:-1]

    @classmethod
    def _get_img_from_event_element(cls, event_element):
        return "https://www.blackcatdc.com" + event_element.find("img")["src"]

    @classmethod
    def _get_link_from_event_element(cls, event_element):
        return event_element.find("a")["href"]

    @classmethod
    def _get_price_from_event_element(cls, event_element):
        return event_element.find("p", class_="show-text").text.strip()

    @classmethod
    def _get_title_from_event_element(cls, event_element):
        return event_element.find("h1", class_="headline").text.strip()


def get_upcoming_events():
    return [
        event
        for scraper in BaseScraper.__subclasses__()
        for event in scraper.get_events()
    ]
