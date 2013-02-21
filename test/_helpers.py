import datetime


class NewDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2012, 12, 10)


class DeferredHelper(object):
    def __init__(self, fire_callback=True, fire_errback=False, data=None):
        self.callbacks = []
        self.errbacks = []
        self.fire_callback = fire_callback
        self.fire_errback = fire_errback
        self.data = data
        self.args = None

    def _fire(self):
        def _walk_func_list(func_list):
            res = None
            for callback in func_list:
                res = callback(self.data)
                if res is None:
                    break

        if self.fire_callback and len(self.callbacks) > 0:
            _walk_func_list(self.callbacks)

        if self.fire_errback and len(self.errbacks) > 0:
            _walk_func_list(self.errbacks)

    def addCallback(self, callback):
        self.callbacks.append(callback)

    def addErrback(self, errback):
        self.errbacks.append(errback)

    def addCallbacks(self, callback, errback):
        self.callbacks.append(callback)
        self.errbacks.append(errback)

    def __call__(self, *args):
        self.args = args
        return self
