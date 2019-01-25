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
