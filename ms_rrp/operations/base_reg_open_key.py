from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar
from struct import pack as struct_pack, unpack as struct_unpack
from contextlib import asynccontextmanager

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.utils import calculate_pad_length, pad as ndr_pad

from ms_rrp.operations import Operation
from ms_rrp.structures.regsam import Regsam
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.base_reg_open_key_options import BaseRegOpenKeyOptions
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


@dataclass
class BaseRegOpenKeyResponse(ClientProtocolResponseBase):
    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> BaseRegOpenKeyResponse:
        return cls(key_handle=data[:20], return_code=Win32ErrorCode(struct_unpack('<I', data[20:24])[0]))

    def __bytes__(self) -> bytes:
        return self.key_handle + struct_pack('<I', self.return_code)


@dataclass
class BaseRegOpenKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_OPEN_KEY

    key_handle: bytes
    sub_key_name: str
    options: BaseRegOpenKeyOptions = BaseRegOpenKeyOptions()
    sam_desired: Regsam = Regsam()

    @classmethod
    def from_bytes(cls, data: bytes) -> BaseRegOpenKeyRequest:

        offset = 20
        ndr_sub_key_name = RRPUnicodeString.from_bytes(data=data[offset:])
        offset += calculate_pad_length(len(ndr_sub_key_name))

        return cls(
            key_handle=data[:20],
            sub_key_name=ndr_sub_key_name.representation,
            options=BaseRegOpenKeyOptions.from_int(struct_unpack('<I', data[offset:offset+4])[0]),
            sam_desired=Regsam.from_int(struct_unpack('<I', data[offset+4:offset+4+4])[0])
        )

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(bytes(RRPUnicodeString(representation=self.sub_key_name))),
            struct_pack('<I', int(self.options)),
            struct_pack('<I', int(self.sam_desired))
        ])


BaseRegOpenKeyResponse.REQUEST_CLASS = BaseRegOpenKeyRequest
BaseRegOpenKeyRequest.RESPONSE_CLASS = BaseRegOpenKeyResponse


@asynccontextmanager
async def base_reg_open_key(
    rpc_connection: RPCConnection,
    request: BaseRegOpenKeyRequest,
    raise_exception: bool = True
) -> BaseRegOpenKeyResponse:
    """
    Perform the BaseRegOpenKey operation.

    :param rpc_connection:
    :param request:
    :param raise_exception:
    :return:
    """

    base_reg_open_key_response: BaseRegOpenKeyResponse = await obtain_response(
        rpc_connection=rpc_connection,
        request=request,
        raise_exception=raise_exception
    )

    # TODO: This should be yielding the response object instead.

    yield base_reg_open_key_response.key_handle

    await base_reg_close_key(
        rpc_connection=rpc_connection,
        request=BaseRegCloseKeyRequest(
            key_handle=base_reg_open_key_response.key_handle
        )
    )
