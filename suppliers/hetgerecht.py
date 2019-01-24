from bs4 import BeautifulSoup
from datetime import datetime
from urllib import request
from .utils import DateFormatter

from .nomssupplier import NomsSupplier

class HetGerecht(NomsSupplier):
    friendly_name = 'Het Gerecht'

    # Note that this URL changes every week, but the old one is kindly redirected.
    # There does not seem to be one without a date in it, unfortunately.
    menu_url = 'https://www.ru.nl/facilitairbedrijf/horeca/het-gerecht-grotiusgebouw/menu-14-18-januari/'

    @staticmethod
    def getMenu(dt=datetime.now()):
        try:
            url = HetGerecht.menu_url
            print("Requesting: " + url)
            response = request.urlopen(url)
        except:
            print("Could not load this week's menu for Het Gerecht")
            return []

        html = response.read()
        bs = BeautifulSoup(html, 'html5lib')
        menu_node = bs.find("div", class_="rol-inhoud")
        if not menu_node:
            print("Could not find menu node for Het Gerecht")
            return []

        nodes = menu_node.find_all(['p', 'li'])
        today = DateFormatter.longDate(dt)
        describes_today = False
        lines = []
        for node in nodes:
            # First, make sure we've found the right date.
            if node.name == 'p':
                # Hang on, does this mean we've got the full set already?
                if describes_today:
                    break

                describes_today = today in node.get_text().lower()
                continue

            # Once we've found our day, start copying lines.
            if describes_today and node.name == 'li':
                lines.append(node.get_text().strip())

        return lines

    @staticmethod
    def isOpen(dt=datetime.now()):
        # Closed during the weekend
        if dt.weekday() > 4:
            return False

        # Monday to Thursday: 11:00 until 19:00
        elif dt.weekday() < 4:
            return dt.hour >= 11 and dt.hour < 19

        # Fridays from 11:00 until 16:00
        elif dt.weekday() == 4:
            return dt.hour >= 11 and dt.hour < 16

        # ... What planet is this?
        else:
            raise ValueError('Encountered an unexpected weekday.')

    @staticmethod
    def willOpen(dt=datetime.now()):
        # Monday to Friday
        if dt.weekday() < 5:
            return dt.hour < 11

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

        # ... What planet is this?
        else:
            raise ValueError('Encountered an unexpected weekday.')

    @staticmethod
    def isOpenForDinner(dt=datetime.now()):
        # Closed on Friday and during the weekend
        if dt.weekday() >= 4:
            return False

        # Monday to Thursday: 17:00 until 19:00
        elif dt.weekday() < 4:
            return dt.hour >= 17 and dt.hour < 19

        # ... What planet is this?
        else:
            raise ValueError('Encountered an unexpected weekday.')

