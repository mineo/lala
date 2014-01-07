try:
    # Python < 2.7
    import unittest2 as unittest
except ImportError:
    import unittest

from lala import config
from ConfigParser import RawConfigParser, NoSectionError
from os import remove


class TestConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config._CFG = RawConfigParser()
        config._FILENAME = None

    def setUp(self):
        for section in config._CFG.sections():
            config._CFG.remove_section(section)

    def test_exists(self):
        config.set("key", "value")
        self.assertEqual("value", config.get("key"))

    def test_set_default_options(self):
        config.set_default_options(stringkey="foo", defaultintkey="1")
        self.assertEqual(config.get("stringkey"), "foo")
        self.assertEqual(config.get_int("defaultintkey"), 1)

    def test_set_default_options_list(self):
        items = ["foo", "bar", "baz"]
        config.set_default_options(defaultlisttest=items)
        self.assertEqual(sorted(config.get_list("defaultlisttest")),
                sorted(items))

    def test_default_doesnt_overwrite(self):
        config.set("not_overwritten_key", 1)
        config.set_default_options(not_overwritten_key=2)
        self.assertEquals(config.get_int("not_overwritten_key"), 1)

    def test_converter_int_setandget(self):
        config.set("intkey", 2)
        self.assertTrue(isinstance(config.get_int("intkey"), int))

    def test_converter_list_setandget(self):
        items = ["foo", "bar", "baz"]
        config.set_list("listkey", items)
        self.assertEqual(sorted(config.get_list("listkey")), sorted(items))

    def test_raises(self):
        self.assertRaises(NoSectionError, config.get, "foo")
