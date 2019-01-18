#!/usr/bin/env python3

import argparse
import locale

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dazeus import DaZeus
from urllib import request


class DateFormatter(object):
    dutchMonths = ['januari', 'februari', 'maart', 'april', 'mei', 'juni',
        'juli', 'augustus', 'september', 'oktober', 'november', 'december']

    dutchDays = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag',
        'zaterdag', 'zondag']
    englishDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
        'Saturday', 'Sunday']

    dutchDaysShort = ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo']
    englishDaysShort = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'so']

    @staticmethod
    def longDate(dt):
        return '{} {} {}'.format(DateFormatter.dutchDays[dt.weekday()], dt.day,
            DateFormatter.dutchMonths[dt.month - 1])


class NomsSupplier(object):
    friendly_name = None

    @staticmethod
    def getMenu(dt=datetime.now()):
        raise NotImplementedError()

    @staticmethod
    def isOpen(dt=datetime.now()):
        raise NotImplementedError()

    @staticmethod
    def willOpen(dt=datetime.now()):
        raise NotImplementedError()

    @staticmethod
    def isOpenForLunch(dt=datetime.now()):
        raise NotImplementedError()

    @staticmethod
    def isOpenForDinner(dt=datetime.now()):
        raise NotImplementedError()


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
        elif dt.weekday() > 5:
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


class Refter(NomsSupplier):
    friendly_name = 'De Refter'

    @staticmethod
    def getMenu(dt=datetime.now()):
        return []

    @staticmethod
    def isOpen(dt=datetime.now()):
        return False

    @staticmethod
    def isOpenForLunch(dt=datetime.now()):
        return Refter.isOpen()

    @staticmethod
    def isOpenForDinner(dt=datetime.now()):
        return Refter.isOpen()


class DaZeusNoms(object):
    suppliers = {
        'gerecht': HetGerecht,
        'umc': RadboudUMC,
    }

    def __init__(self, address, verbose = False):
        self.dazeus = DaZeus(address, verbose)
        self.dazeus.subscribe_command("noms", self.handleMessage)

    def listen(self):
        self.dazeus.listen()

    def handleMessage(self, event, reply):
        # Ready available suppliers
        suppliers = DaZeusNoms.suppliers.keys()
        params = event['params']

        # Ensure a restaurant is set.
        if len(params) < 6:
            reply('Where would you like to eat? I know the menu for: ' + ', '.join(suppliers))
            return

        # Ensure it is one we know.
        supplier = params[5].lower()
        if supplier not in suppliers:
            reply('I don\'t have a menu for that place... How about one of these: ' + ', '.join(suppliers))
            return

        # Did we say when we'd like to eat?
        now = datetime.now();
        if len(params) >= 7:
            when = params[6]
            # Today?
            if when in ['today', 'vandaag', 'nu', 'vanmiddag', 'vanavond']:
                dt = now
            # Tomorrow?
            elif when in ['tomorrow', 'morgen']:
                dt = now + timedelta(days=1)
            # Day of the week?
            else:
                when = when[0:2]
                print('Looking for ' + when)
                if when in DateFormatter.dutchDaysShort:
                    when = DateFormatter.dutchDaysShort.index(when)
                elif when in DateFormatter.englishDaysShort:
                    when = DateFormatter.englishDaysShort.index(when)
                else:
                    when = None

                dt = now
                if when >= 0:
                    offset = when - dt.weekday()
                    dt += timedelta(days=offset)
                    dt.replace(hour=12)

        # Fall back to today
        else:
            dt = now

        # So, what day is this, again?
        concerningDay = 'today' if dt == now else DateFormatter.englishDays[dt.weekday()]

        # Dial our supplier...
        supplier = DaZeusNoms.suppliers[supplier]
        if not (supplier.isOpen(dt) or supplier.willOpen(dt)):
            excuse = 'Sorry, ' + supplier.friendly_name
            if dt == now:
                excuse += ' has closed for the day...'
            else:
                excuse += ' is not open on ' + concerningDay + '...'

            reply(excuse)
            return

        # Fetch the menu!
        menu = supplier.getMenu(dt)
        if not menu:
            excuse = 'Sorry, I was unable to get a menu for ' + supplier.friendly_name + ' for ' + concerningDay
            reply(excuse)

        # Announce it properly...
        reply('Here\'s the menu for ' + supplier.friendly_name + ' for ' + concerningDay + ':')

        # Now, pass it on to our faithful user.
        for line in menu:
            reply(line)

        # Finally... can we get this now?
        if dt == now:
            # Are we open for lunch?
            if supplier.isOpenForLunch():
                reply(supplier.friendly_name + ' is open for lunch right now.')

            # What about dinner?
            elif supplier.isOpenForDinner():
                reply(supplier.friendly_name + ' is open for dinner right now.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DaZeus noms plugin.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--address', required=True, help='Address of the DaZeus instance to connect to. ' +
        'Use either `unix:/path/to/file` or `tcp:host:port`.')
    parser.add_argument('-v', '--verbose', default=False, help='Increase output verbosity', action='store_true')

    # Fetch command line arguments.
    args = parser.parse_args()

    # Run the bot.
    bot = DaZeusNoms(args.address, args.verbose)
    bot.listen()
