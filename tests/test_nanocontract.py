# Copyright (c) Hathor Labs and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from hathorlib import Transaction
from hathorlib.headers import NanoHeader
from hathorlib.headers.nano_header import NanoHeaderAction
from hathorlib.nanocontracts.types import NCActionType


class NCNanoContractTestCase(unittest.TestCase):
    def _get_nc(self) -> Transaction:
        nc = Transaction()
        nc.weight = 1
        nc.timestamp = 123456
        nano_header = NanoHeader(
            tx=nc,
            nc_actions=[
                NanoHeaderAction(
                    type=NCActionType.DEPOSIT,
                    token_index=0,
                    amount=123,
                ),
            ],
            nc_id=b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            nc_method='initialize',
            # ['string', 1]
            nc_args_bytes=b'\x00\x06string\x00\x04\x00\x00\x00\x01',
            nc_pubkey=b'\x020\xc1K\xb8\xc4fO>\xb7\x96a\xdeN\x96\x92\xcd\x1c\xa8\xa3]'
                      b'\xfeZ\xf7}\x95\x99\xb0\x1cBE\xc8\x90',
            nc_signature=b'0F\x02!\x00\x9c\xfey\xb1C\x9eAJ\x9eU~\xe3\xaf\xfcQ' \
                         b'\xf6\xf0`g\x1b0\xb6\xca\x1b\xed\x83:N\xa0\x98\xd2' \
                         b'\xdf\x02!\x00\xbe\xf85\xf6O`\xfed`Ip\xe2a\xc4\x03vv' \
                         b'\xec\x94\ny?\xde\x90\xc3\x12\x9c\xd8\xdd\xd8\xe5\r'
        )
        nc.headers = [nano_header]
        return nc

    def test_serialization(self) -> None:
        nc = self._get_nc()

        nc_bytes = bytes(nc)
        nc2 = Transaction.create_from_struct(nc_bytes)
        self.assertEqual(nc_bytes, bytes(nc2))
        nano_header1 = nc.get_nano_header()
        nano_header2 = nc2.get_nano_header()

        self.assertEqual(nano_header1.nc_id, nano_header2.nc_id)
        self.assertEqual(nano_header1.nc_method, nano_header2.nc_method)
        self.assertEqual(nano_header1.nc_args_bytes, nano_header2.nc_args_bytes)
        self.assertEqual(nano_header1.nc_pubkey, nano_header2.nc_pubkey)
        self.assertEqual(nano_header1.nc_signature, nano_header2.nc_signature)
        self.assertEqual(nano_header1.nc_actions, nano_header2.nc_actions)
