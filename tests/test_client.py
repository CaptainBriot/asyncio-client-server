import unittest.mock
import asyncio
import asynctest

import client


class TestMain(unittest.TestCase):
    @unittest.mock.patch('asyncio.get_event_loop')
    @unittest.mock.patch('client.parse_args')
    @unittest.mock.patch('common.init_logging')
    def test_cli(self, mock_init_logging, mock_parse_args, mock_get_event_loop):
        class Options:
            period = 10

        mock_parse_args.return_value = Options()

        client.main()

        self.assertIsNone(mock_init_logging.assert_called_once())
        self.assertIsNone(mock_parse_args.assert_called_once())
        self.assertEqual(len(mock_get_event_loop.mock_calls), 4)


class TestThrottlingClientStart(asynctest.TestCase):
    def setUp(self):
        self.client = client.ThrottlingClient('127.0.0.1', 8888, 10)

    def test_send(self):
        reader = asynctest.mock.MagicMock(asyncio.StreamReader)
        writer = asynctest.mock.MagicMock(asyncio.StreamWriter)

        with asynctest.mock.patch('asyncio.open_connection', return_value=(reader, writer)):
            asyncio.get_event_loop().run_until_complete(self.client.send())

        self.assertEqual(reader.mock_calls, [])
        self.assertEqual(writer.mock_calls, [asynctest.mock.call.write(b'0'), asynctest.mock.call.close()])

    def test_send_request_connection_error(self):
        with asynctest.mock.patch('asyncio.open_connection', side_effect=ConnectionError):
            asyncio.get_event_loop().run_until_complete(self.client.send())


class TestBasicRateLimitingProtocol(asynctest.TestCase):
    def setUp(self):
        self.callback = unittest.mock.MagicMock()
        self.protocol = client.BasicRateLimitingProtocol(self.callback, 10)

    def test_start(self):
        new = asynctest.mock.MagicMock(side_effect=[None, ValueError])
        with asynctest.mock.patch('asyncio.ensure_future', new=new) as mock_ensure_future:
            with self.assertRaises(ValueError):
                asyncio.get_event_loop().run_until_complete(self.protocol.start())
            print(mock_ensure_future.mock_calls)
            self.assertEqual(len(mock_ensure_future.mock_calls), 3)
            self.assertEqual(self.callback.mock_calls, [unittest.mock.call(), unittest.mock.call()])


class TestTokenBucketRateLimitingProtocol(asynctest.TestCase):
    def setUp(self):
        self.callback = unittest.mock.MagicMock()
        self.protocol = client.TokenBucketRateLimitingProtocol(self.callback, 10)

    def test_init(self):
        self.assertEqual(self.protocol.max_tokens, 10)
        protocol = client.TokenBucketRateLimitingProtocol(self.callback, 0.5)
        self.assertEqual(protocol.max_tokens, 1)

    def test_add_new_tokens(self):
        self.protocol.updated_at = 0
        self.assertEqual(self.protocol.tokens, 0)
        self.protocol.add_new_tokens()
        self.assertEqual(self.protocol.tokens, 10)

    async def test_wait(self):
        self.protocol.updated_at = 0
        self.assertEqual(self.protocol.tokens, 0)
        await self.protocol.wait()
        self.assertEqual(self.protocol.tokens, 9)

    def test_start(self):
        new = asynctest.mock.MagicMock(side_effect=[None, ValueError])
        self.protocol.tokens = 10
        with asynctest.mock.patch('asyncio.ensure_future', new=new) as mock_ensure_future:
            with self.assertRaises(ValueError):
                asyncio.get_event_loop().run_until_complete(self.protocol.start())
            print(mock_ensure_future.mock_calls)
            self.assertEqual(len(mock_ensure_future.mock_calls), 3)
            self.assertEqual(self.callback.mock_calls, [unittest.mock.call(), unittest.mock.call()])
