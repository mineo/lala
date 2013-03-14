from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from lala.main import LalaOptions, getService

class LalaServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "lala"
    description = "IRC Bot"
    options = LalaOptions

    def makeService(self, options):
        return getService(options)

serviceMaker = LalaServiceMaker()
