from datetime import datetime

from .nomssupplier import NomsSupplier

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
