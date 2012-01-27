import unittest

from lala import config
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from os import remove

class TestConfig(unittest.TestCase):
    def setUp(self):
        config._CFG = SafeConfigParser()
        config._FILENAME = "foobar.txt"
        config._CFG.read(config._FILENAME)

    def test_exists(self):
        config.set("key", "value")
        self.assertEqual("value", config.get("key"))

    def test_raises(self):
        self.assertRaises(NoSectionError, config.get, "foo")

        config._CFG.add_section("testsection")
        self.assertRaises(NoOptionError, config._get, "testsection", "foo")

    @classmethod
    def tearDownClass(cls):
        remove(config._FILENAME)
