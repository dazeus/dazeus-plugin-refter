from bs4 import BeautifulSoup
from datetime import datetime
from urllib import request
from .utils import DateFormatter

from .nomssupplier import NomsSupplier

class RadboudUMC(NomsSupplier):
    friendly_name = 'Radboud UMC'

    # Concat with slugified long date, e.g. 'donderdag-17-januari'
    menu_prefix = 'https://www.radboudumc.nl/patientenzorg/voorzieningen/eten-en-drinken/menu-van-de-dag/'

    @staticmethod
    def getMenu(dt=datetime.now()):
        try:
            url = RadboudUMC.menu_prefix + DateFormatter.longDate(dt).replace(' ', '-')
            print("Requesting: " + url)
            response = request.urlopen(url)
        except:
            print("Could not load today's menu for RadboudUMC")
            return []

        html = response.read()
        bs = BeautifulSoup(html, 'html5lib')
        menu_node = bs.find("ul", class_="List-Clear List-Divided js-Accordion")
        if not menu_node:
            return []

        menu_entries = menu_node.find_all("li", recursive=False)
        menu_lines = []
        for entry in menu_entries:
            category = entry.find('button').get_text().strip()
            line = category + ': '

            dish_nodes = entry.find_all('li')
            dishes = []
            for dish in dish_nodes:
                dishes.append(dish.get_text().strip())

            line += ', '.join(dishes)
            menu_lines.append(line)

        return menu_lines

    @staticmethod
    def isOpen(dt=datetime.now()):
        # Monday to Friday: 08:00 until 20:00
        if dt.weekday() < 5:
            return dt.hour >= 8 and dt.hour < 20

        # Weekends from 11:00 until 20:00
        elif dt.weekday() >= 5:
            return dt.hour >= 11 and dt.hour < 20

        # ... What planet is this?
        else:
            raise ValueError('Encountered an unexpected weekday.')

    @staticmethod
    def willOpen(dt=datetime.now()):
        if dt.weekday() < 5:
            return dt.hour < 8
        elif dt.weekday() >= 5:
            return dt.hour < 11
        else:
            raise ValueError('Encountered an unexpected weekday.')

    @staticmethod
    def isOpenForLunch(dt=datetime.now()):
        # Every day from 11.30 until 14.00
        return (dt.hour == 11 and dt.minute >= 30) or (dt.hour > 11 and dt.hour < 14)

    @staticmethod
    def isOpenForDinner(dt=datetime.now()):
        # Every day from 16.30 until 19.30.
        (h, m) = (dt.hour, dt.minute)
        return (h == 16 and m >= 30) or (h > 16 and h < 19) or (h == 19 and m < 30)
