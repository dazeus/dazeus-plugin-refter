from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib import request
from .utils import DateFormatter

from .nomssupplier import NomsSupplier

class Refter(NomsSupplier):
    friendly_name = 'De Refter'
    menu_url = 'https://www.ru.nl/facilitairbedrijf/horeca/refter/menu-soep-week/'

    @staticmethod
    def getMenu(dt=datetime.now()):
        try:
            url = Refter.menu_url
            print("Requesting: " + url)
            response = request.urlopen(url)
        except:
            print("Could not load this week's menu for " + Refter.friendly_name)
            return []

        html = response.read()
        bs = BeautifulSoup(html, 'html5lib')
        menu_node = bs.find("div", class_="rol-inhoud")
        if not menu_node:
            print("Could not find menu node for " + Refter.friendly_name)
            return []

        nodes = menu_node.find_all('p')
        today = DateFormatter.longDate(dt)
        lines = []
        for node in nodes:
            # Continue until we have found a node that contains today's date.
            if not today in node.get_text().lower():
                continue

            # The menu is actually in a neighbouring list.
            menu = nodes[0].next_sibling.next_element

            # Copy the lines without any HTML.
            for menu_entry in menu.find_all('li'):
                lines.append(menu_entry.get_text().strip())

        return lines

    @staticmethod
    def isOpen(dt=datetime.now()):
        # Monday to Friday
        if dt.weekday() < 5:
            return (dt.hour == 7 and dt.minute < 30) or (dt.hour >= 8 and dt.hour < 20)

        # Closed during the weekend
        elif dt.weekday() >= 5:
            return False

    @staticmethod
    def willOpen(dt=datetime.now()):
        # Monday to Friday
        if dt.weekday() < 5:
            return dt.hour < 7 or (dt.hour == 7 and dt.minute < 30)

        # Closed during the weekend
        elif dt.weekday() >= 5:
            return False

    @staticmethod
    def isOpenForLunch(dt=datetime.now()):
       return Refter.isOpen(dt);

    @staticmethod
    def isOpenForDinner(dt=datetime.now()):
        return Refter.isOpen(dt);
