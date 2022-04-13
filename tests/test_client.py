"""
Copyright (c) Hathor Labs and its affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import asyncio
from unittest.mock import MagicMock, Mock

import asynctest

from hathorlib.client import HathorClient


class ClientTestCase(asynctest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.client = HathorClient(server_url='')
        self.loop.run_until_complete(self.client.start())

        self.client._session = Mock()

    def _run_all_pending_events(self):
        """Run all pending events."""
        # pending = asyncio.all_tasks(self.loop)
        # self.loop.run_until_complete(asyncio.gather(*pending))
        async def _fn():
            pass
        future = asyncio.ensure_future(_fn())
        self.loop.run_until_complete(future)

    def test_version(self):
        self.client._session.get = MagicMock(return_value=None)

    async def test_push_tx_or_block_error(self):
        # Preparation
        class MockResponse:
            def __init__(self):
                self.status = 500

            async def text(self):
                return "Test Response"

        async def post_mock(url, json):
            return MockResponse()

        self.client._session.post = post_mock

        # Execution
        with self.assertRaises(RuntimeError):
            await self.client.push_tx_or_block(bytes('123123', 'utf8'))
