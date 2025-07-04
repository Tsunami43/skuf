import os

from tests.conftest import SettingsExample, TestSetUpBaseSettings


class TestBaseSettings(TestSetUpBaseSettings):
    def test_string_setting(self):
        s = SettingsExample()
        self.assertEqual(s.token, "abc123")

    def test_int_setting(self):
        s = SettingsExample()
        self.assertEqual(s.retries, 3)

    def test_bool_setting(self):
        s = SettingsExample()
        self.assertTrue(s.debug)

    def test_float_setting(self):
        s = SettingsExample()
        self.assertAlmostEqual(s.timeout, 2.5)

    def test_list_str_setting(self):
        s = SettingsExample()
        self.assertEqual(s.servers, ["server1", "server2", "server3"])

    def test_list_int_setting(self):
        s = SettingsExample()
        self.assertEqual(s.ports, [8000, 8001, 8002])

    def test_is_loaded_method(self):
        s = SettingsExample()
        self.assertFalse(s.is_loaded("token"))
        _ = s.token
        self.assertTrue(s.is_loaded("token"))

    def test_dict_method_returns_all_fields(self):
        s = SettingsExample()
        expected_keys = ["token", "retries", "debug", "timeout", "servers", "ports"]
        d = s.dict()
        self.assertEqual(set(d.keys()), set(expected_keys))
        self.assertEqual(d["token"], "abc123")
        self.assertEqual(d["retries"], 3)

    def test_missing_variable_raises(self):
        os.environ.pop("TOKEN", None)
        with self.assertRaises(AttributeError):
            _ = SettingsExample().token
