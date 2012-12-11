import datetime


class NewDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2012, 12, 10)


class DeferredHelper(object):
    def __init__(self, fire_callback=True, fire_errback=False, data=None):
        self.callback = None
        self.errback = None
        self.fire_callback = fire_callback
        self.fire_errback = fire_errback
        self.data = data
        self.args = None

    def _fire(self):
        if self.fire_callback and self.callback is not None:
            self.callback(self.data)

        if self.fire_errback and self.errback is not None:
            self.errback(self.data)

    def addCallback(self, callback):
        self.callback = callback
        self._fire()

    def addCallbacks(self, callback, errback):
        self.callback = callback
        self.errback = errback
        self._fire()

    def __call__(self, *args):
        self.args = args
        return self
