from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib import request
from .utils import DateFormatter

from .nomssupplier import NomsSupplier

class FNWI(NomsSupplier):
    friendly_name = 'FNWI'

    # Note that this URL changes every week, but the old one is kindly redirected.
    # There does not seem to be one without a date in it, unfortunately.
    menu_url = 'https://www.ru.nl/facilitairbedrijf/horeca/restaurant-fnwi/menu-25-29-maart/'

    @staticmethod
    def getMenu(dt=datetime.now()):
        try:
            url = FNWI.menu_url
            print("Requesting: " + url)
            response = request.urlopen(url)
        except:
            print("Could not load this week's menu for " + FNWI.friendly_name)
            return []

        html = response.read()
        bs = BeautifulSoup(html, 'html5lib')
        menu_node = bs.find("div", class_="rol-inhoud")
        if not menu_node:
            print("Could not find menu node for " + FNWI.friendly_name)
            return []

        nodes = menu_node.find_all('p')
        today = DateFormatter.longDate(dt)
        tomorrow = DateFormatter.longDate(dt + timedelta(days=1))
        describes_today = False
        describes_tomorrow = False
        lines = []
        for node in nodes:
            # Continue until we have found today's menu.
            if not describes_today:
                describes_today = today in node.get_text().lower()
                continue

            describes_tomorrow = tomorrow in node.get_text().lower()
            if describes_tomorrow:
                break

            # Once we've found our day, start copying lines.
            lines.append(node.get_text().strip())

        # As there usually is only one menu, concat any trailing information into one line.
        lines = [" ".join(lines)]

        return lines

    @staticmethod
    def isOpen(dt=datetime.now()):
        FNWI.isOpenForLunch(dt)

    @staticmethod
    def willOpen(dt=datetime.now()):
        # Monday to Friday
        if dt.weekday() < 5:
            return dt.hour < 12

        # Closed during the weekend
        elif dt.weekday() >= 5:
            return False

    @staticmethod
    def isOpenForLunch(dt=datetime.now()):
        # Closed during the weekend
        if dt.weekday() > 4:
            return False

        # Monday to Friday: 12:00 until 13:30
        elif dt.weekday() <= 4:
            return dt.hour == 12 or (dt.hour == 13 and dt.minute < 30)

    @staticmethod
    def isOpenForDinner(dt=datetime.now()):
        return False
