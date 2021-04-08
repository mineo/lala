from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from lala.main import LalaOptions, getService


@implementer(IServiceMaker, IPlugin)
class LalaServiceMaker(object):
    tapname = "lala"
    description = "IRC Bot"
    options = LalaOptions

    def makeService(self, options):
        return getService(options)

serviceMaker = LalaServiceMaker()
