from datetime import datetime
from .utils import DateFormatter

from .nomssupplier import NomsSupplier

class DeFest(NomsSupplier):
    friendly_name = 'Cafetaria De Fest'

    @staticmethod
    def getMenu(dt=datetime.now()):
        menu_lines = ["Ook vandaag maakt de Fest weer lekkere frietjes, pizza's, enzovoort."]

        if dt.weekday() == 0 or dt.weekday() == 1:
            menu_lines.append("Vandaag is het ook nog eens pizzadag: alle pizza's tussen de 6 en 8 euro!")
        elif dt.weekday() == 2 or dt.weekday() == 3:
            menu_lines.append("Vandaag is het ook nog eens schoteldag: alle schotels 2 euro korting!")

        return menu_lines

    @staticmethod
    def isOpen(dt=datetime.now()):
        return dt.hour >= 11 and dt.hour < 23

    @staticmethod
    def willOpen(dt=datetime.now()):
        return dt.hour < 11

    @staticmethod
    def isOpenForLunch(dt=datetime.now()):
        return DeFest.isOpen()

    @staticmethod
    def isOpenForDinner(dt=datetime.now()):
        return DeFest.isOpen()
