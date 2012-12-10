import datetime

class NewDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2012, 12, 10)
