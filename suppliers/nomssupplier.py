from datetime import datetime

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
