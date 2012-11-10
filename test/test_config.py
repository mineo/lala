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

    def test_set_default_options(self):
        config.set_default_options(stringkey="foo", defaultintkey="1")
        self.assertEqual(config.get("stringkey"), "foo")
        self.assertEqual(config.get_int("defaultintkey"), 1)

    def test_set_default_options_list(self):
        config.set_default_options(defaultlisttest=["foo", "bar"])
        self.assertItemsEqual(config.get_list("defaultlisttest"), ["foo", "bar"])

    def test_default_doesnt_overwrite(self):
        config.set("not_overwritten_key", 1)
        config.set_default_options(not_overwritten_key=2)
        self.assertEquals(config.get_int("not_overwritten_key"), 1)

    def test_converter_int_setandget(self):
        config.set("intkey", 2)
        self.assertTrue(isinstance(config.get_int("intkey"), int))

    def test_converter_list_setandget(self):
        config.set_list("listkey", ["foo", "bar", "baz"])
        self.assertItemsEqual(config.get_list("listkey"),
                              ["foo", "bar", "baz"])

    def test_converter_list_get_with_default(self):
        config.set_list("listkey2", ["1", "2", "3"])
        self.assertItemsEqual(config.get_list("listkey2"), ["1", "2", "3"])

    def test_raises(self):
        self.assertRaises(NoSectionError, config.get, "foo")

        config._CFG.add_section("testsection")
        self.assertRaises(NoOptionError, config._get, "testsection", "foo")

    @classmethod
    def tearDownClass(cls):
        remove(config._FILENAME)
