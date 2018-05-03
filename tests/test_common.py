import unittest.mock
import logging

import common


class TestInitLogging(unittest.TestCase):
    @unittest.mock.patch('logging.root.addHandler')
    @unittest.mock.patch('logging.root.setLevel')
    def test_init_logging(self, mock_set_level, mock_add_handler):
        common.init_logging()
        self.assertEqual(mock_set_level.mock_calls, [unittest.mock.call(logging.DEBUG)])
        self.assertIsNone(mock_add_handler.assert_called())
