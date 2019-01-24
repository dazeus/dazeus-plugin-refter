#!/usr/bin/env python3

import argparse

from datetime import datetime, timedelta
from dazeus import DaZeus
from suppliers import HetGerecht, RadboudUMC
from suppliers.utils import DateFormatter

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
                dt = dt.replace(hour=12)
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
                    dt = dt.replace(hour=12)

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
            return

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
