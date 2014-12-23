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


class DeferredHelper(Deferred):
    def __init__(self, data=None):
        Deferred.__init__(self)
        self.data = data

    def callback(self, result=None):
        if result is None:
            result = self.data
        return Deferred.callback(self, result)

    def errback(self, failure=None):
        if failure is None:
            failure = self.data
        return Deferred.errback(self, failure)

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
