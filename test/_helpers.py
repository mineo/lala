import datetime
import mock


from functools import wraps
from twisted.internet.defer import Deferred


class NewDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2012, 12, 10)


class NewDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return cls(2012, 12, 10, 00, 00, 00, 00, None)


class DeferredHelper(object):
    def __init__(self, data=None):
        self.data = data
        self.deferred = Deferred()
        self.addCallback = self.deferred.addCallback
        self.addCallbacks = self.deferred.addCallbacks
        self.addErrback = self.deferred.addErrback

    def callback(self, result=None):
        if result is None:
            result = self.data
        self.deferred.callback(result)

    def errback(self, failure=None):
        if failure is None:
            failure = self.data
        self.deferred.errback(failure)

    def __call__(self, *args):
        self.args = args
        return self


def mock_is_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with mock.patch("lala.pluginmanager.is_admin") as mocked:
            mocked.return_value = True
            return f(*args, **kwargs)
    return wrapper
