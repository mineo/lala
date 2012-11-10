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

    def test_default(self):
        self.assertEqual("default", config.get("testkey", "default"))

    def test_converter_int_setandget(self):
        config.set("intkey", "2")
        self.assertTrue(isinstance(config.get_int("intkey"), int))

    def test_converter_int_get_with_default(self):
        self.assertTrue(isinstance(config.get_int("intkey2", 3), int))

    def test_converter_list_setandget(self):
        config.set_list("listkey", ["foo", "bar", "baz"])
        self.assertItemsEqual(config.get_list("listkey"),
                              ["foo", "bar", "baz"])

    def test_converter_list_get_with_default(self):
        self.assertItemsEqual(config.get_list("listkey2", [1, 2, 3]),
                              ["1", "2", "3"])

    def test_raises(self):
        self.assertRaises(NoSectionError, config.get, "foo")

        config._CFG.add_section("testsection")
        self.assertRaises(NoOptionError, config._get, "testsection", "foo")

    @classmethod
    def tearDownClass(cls):
        remove(config._FILENAME)
