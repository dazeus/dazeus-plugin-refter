#!/usr/bin/env python3

import argparse
import locale

from bs4 import BeautifulSoup
from datetime import datetime
# from dazeus import DaZeus
from urllib import request


class DateFormatter(object):
    dutchMonths = ['januari', 'februari', 'maart', 'april', 'mei', 'juni',
        'juli', 'augustus', 'september', 'oktober', 'november', 'december']

    dutchDays = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag',
        'zaterdag', 'zondag']

    @staticmethod
    def longDate(dt):
        return '{} {} {}'.format(DateFormatter.dutchDays[dt.weekday()], dt.day,
            DateFormatter.dutchMonths[dt.month - 1])


class NomsSupplier(object):
    @staticmethod
    def getMenu(dt=datetime.now()):
        raise NotImplementedError()

    @staticmethod
    def isOpen():
        raise NotImplementedError()

    @staticmethod
    def isOpenForLunch():
        raise NotImplementedError()

    @staticmethod
    def isOpenForDinner():
        raise NotImplementedError()


class HetGerecht(NomsSupplier):
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
        bs = BeautifulSoup(html)
        menu_node = bs.find("div", class_="rol-inhoud")
        if not menu_node:
            return []

        nodes = menu_node.find_all(['p', 'li'])
        today = DateFormatter.longDate(dt)
        describes_today = False
        lines = []
        for node in nodes:
            # First, make sure we've found the right date.
            if node.name == 'p':
                describes_today = today in node.get_text().lower()
                continue

            # Once we've found our day, start copying lines.
            if describes_today and node.name == 'li':
                lines.append(node.get_text().strip())

        return lines

    @staticmethod
    def isOpen():
        # ma t/m do van 11.00-19.00 uur
        # vr. van 11.00-16.00 uur
        pass

    @staticmethod
    def isOpenForLunch():
        # Maaltijden zijn verkrijgbaar tussen 12.00 - 13.30 uur
        # weekenden gesloten
        return HetGerecht.isOpen()

    @staticmethod
    def isOpenForDinner():
        # ma t/m do van 17.00 - 19.00 uur
        # vrijdag en weekenden gesloten
        return HetGerecht.isOpen()


class RadboudUMC(NomsSupplier):
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
        bs = BeautifulSoup(html)
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
    def isOpen():
        # maandag tot en met vrijdag geopend van 08.00 tot 20.00 uur.
        # In het weekend van 11.00 tot 20.00 uur.
        pass

    @staticmethod
    def isOpenForLunch():
        # Lunch wordt geserveerd van 11.30 tot 14.00 uur
        pass

    @staticmethod
    def isOpenForDinner():
        # Diner van 16.30 tot 19.30 uur.
        pass


class Refter(NomsSupplier):
    @staticmethod
    def getMenu(dt=datetime.now()):
        return []

    @staticmethod
    def isOpen():
        return False

    @staticmethod
    def isOpenForLunch():
        return Refter.isOpen()

    @staticmethod
    def isOpenForDinner():
        return Refter.isOpen()


class DaZeusNoms(object):
    def __init__(self, address, verbose = False):
        self.dazeus = DaZeus(address, verbose)
        self.dazeus.subscribe_command("noms", self.handleMessage)

    def handleMessage(self, event, message):
        self.reply("Not actually implemented yet...")

    def sendReply(self, msg):
        self.reply(msg)

    def listen(self):
        self.dazeus.listen()


"""
# Optionally run the bot.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DaZeus noms plugin.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--address', required=True, help='Address of the DaZeus instance to connect to. ' +
        'Use either `unix:/path/to/file` or `tcp:host:port`.')
    parser.add_argument('-v', '--verbose', default=False, help='Increase output verbosity', action='store_true')

    # Fetch command line arguments.
    args = parser.parse_args()

    # Run the bot.
    bot = DaZeusNoms(args.login, args.password, args.address, args.verbose)
    noms.listen()
"""
