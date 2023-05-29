# Copyright 2023 Hathor Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import NamedTuple, Tuple

from hathorlib.base_transaction import TxVersion
from hathorlib.transaction import Transaction
from hathorlib.utils import int_to_bytes, unpack, unpack_len

NC_VERSION = 1


class NCCallInfo(NamedTuple):
    """This tuple carries the pieces of information serialized inside transactions."""
    version: int
    id: bytes
    method: str
    args_bytes: bytes
    pubkey: bytes
    signature: bytes


class NanoContract(Transaction):
    """NanoContract vertex to be placed on the DAG of transactions."""

    MIN_NUM_INPUTS = 0

    def __init__(self) -> None:
        super().__init__()

        self.version = TxVersion.NANO_CONTRACT

        # nc_id equals to the blueprint_id when a Nano Contract is being created.
        # nc_id equals to the nanocontract_id when a method is being called.
        self.nc_id: bytes = b''

        # Name of the method to be called. When creating a new Nano Contract, it must be equal to 'initialize'.
        self.nc_method: str = ''

        # Serialized arguments to nc_method.
        self.nc_args_bytes: bytes = b''

        # Pubkey and signature of the transaction owner / caller.
        self.nc_pubkey: bytes = b''
        self.nc_signature: bytes = b''

    ################################
    # Methods for Transaction
    ################################

    def get_funds_fields_from_struct(self, buf: bytes) -> bytes:
        buf = super().get_funds_fields_from_struct(buf)

        call_info, buf = NanoContract.deserialize_method_call(buf)
        self.nc_id = call_info.id
        self.nc_method = call_info.method
        self.nc_args_bytes = call_info.args_bytes
        self.nc_pubkey = call_info.pubkey
        self.nc_signature = call_info.signature

        return buf

    @classmethod
    def deserialize_method_call(cls, buf: bytes) -> Tuple[NCCallInfo, bytes]:
        """Deserialize method call information from a serialized transaction."""
        (nc_version,), buf = unpack('!B', buf)
        if nc_version != NC_VERSION:
            raise ValueError('unknown nanocontract version: {}'.format(nc_version))

        nc_id, buf = unpack_len(32, buf)
        (nc_method_len,), buf = unpack('!B', buf)
        nc_method, buf = unpack_len(nc_method_len, buf)
        (nc_args_bytes_len,), buf = unpack('!H', buf)
        nc_args_bytes, buf = unpack_len(nc_args_bytes_len, buf)
        (nc_pubkey_len,), buf = unpack('!B', buf)
        nc_pubkey, buf = unpack_len(nc_pubkey_len, buf)
        (nc_signature_len,), buf = unpack('!B', buf)
        nc_signature, buf = unpack_len(nc_signature_len, buf)

        decoded_nc_method = nc_method.decode('ascii')

        return NCCallInfo(
            version=nc_version,
            id=nc_id,
            method=decoded_nc_method,
            args_bytes=nc_args_bytes,
            pubkey=nc_pubkey,
            signature=nc_signature,
        ), buf

    def get_funds_struct(self) -> bytes:
        struct_bytes = super().get_funds_struct()
        struct_bytes += self.serialize_method_call()
        return struct_bytes

    def serialize_method_call(self, *, skip_signature: bool = False) -> bytes:
        """Serialize the method call as part of a transaction serialization."""
        encoded_method = self.nc_method.encode('ascii')

        ret = []
        ret.append(int_to_bytes(NC_VERSION, 1))
        ret.append(self.nc_id)
        ret.append(int_to_bytes(len(self.nc_method), 1))
        ret.append(encoded_method)
        ret.append(int_to_bytes(len(self.nc_args_bytes), 2))
        ret.append(self.nc_args_bytes)
        ret.append(int_to_bytes(len(self.nc_pubkey), 1))
        ret.append(self.nc_pubkey)
        if not skip_signature:
            ret.append(int_to_bytes(len(self.nc_signature), 1))
            ret.append(self.nc_signature)
        else:
            ret.append(int_to_bytes(0, 1))
        return b''.join(ret)
