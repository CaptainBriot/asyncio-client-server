import unittest.mock
import asyncio
import asynctest

import server


class TestMain(unittest.TestCase):
    @unittest.mock.patch('server.TrackerServer.start')
    @unittest.mock.patch('asyncio.get_event_loop')
    @unittest.mock.patch('common.init_logging')
    def test_cli(self, mock_init_logging, mock_get_event_loop, mock_start):
        server.main()
        self.assertIsNone(mock_start.assert_called_once())
        self.assertIsNone(mock_init_logging.assert_called_once())
        self.assertEqual(len(mock_get_event_loop.mock_calls), 4)


class TestTrackerServer(asynctest.TestCase):
    async def setUp(self):
        self.server = server.TrackerServer('127.0.0.1', 8888)


class TestTrackerServerHandleRequest(TestTrackerServer):
    @unittest.mock.patch('uuid.uuid4', new=unittest.mock.MagicMock(return_value='123abc'))
    def test_handle_request(self):
        asyncio.get_event_loop().run_until_complete(self.server.handle_request())
        print(self.server.requests)
        self.assertEqual(self.server.requests, {'123abc'})


class TestTrackerServerStart(TestTrackerServer):
    def test_start(self):
        with asynctest.mock.patch('asyncio.ensure_future') as mock_ensure_future:
            self.server.start()
            print(mock_ensure_future.mock_calls)
            self.assertEqual(len(mock_ensure_future.mock_calls), 2)


class TestTrackerServerLogRequests(TestTrackerServer):
    def test_start(self):
        new = asynctest.mock.MagicMock(side_effect=[None, ValueError])
        with asynctest.mock.patch('logging.Logger.info', new=new) as mock_log:
            with self.assertRaises(ValueError):
                asyncio.get_event_loop().run_until_complete(self.server.log_numbers_requests_per_second())
            print(mock_log.mock_calls)
            self.assertEqual(len(mock_log.mock_calls), 3)
