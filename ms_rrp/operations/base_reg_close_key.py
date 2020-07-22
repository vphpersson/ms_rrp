from __future__ import annotations
from dataclasses import dataclass
from abc import ABC
from typing import Type, ClassVar
from enum import Enum
from struct import pack as struct_pack, unpack as struct_unpack

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response

from ms_rrp.operations import Operation


@dataclass
class BaseRegCloseKeyResponse(ClientProtocolResponseBase):
    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> BaseRegCloseKeyResponse:
        return cls(key_handle=data[:20], return_code=Win32ErrorCode(struct_unpack('<I', data[20:24])[0]))

    def __bytes__(self) -> bytes:
        return self.key_handle + struct_pack('<I', self.return_code)


@dataclass
class BaseRegCloseKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_CLOSE_KEY

    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> BaseRegCloseKeyRequest:
        return cls(key_handle=data[:20])

    def __bytes__(self) -> bytes:
        return self.key_handle


BaseRegCloseKeyResponse.REQUEST_CLASS = BaseRegCloseKeyRequest
BaseRegCloseKeyRequest.RESPONSE_CLASS = BaseRegCloseKeyResponse


async def base_reg_close_key(
    rpc_connection: RPCConnection,
    request: BaseRegCloseKeyRequest,
    raise_exception: bool = True
) -> BaseRegCloseKeyResponse:
    """
    Perform the BaseRegCloseKey operation.

    :param rpc_connection:
    :param request:
    :param raise_exception:
    :return:
    """

    return await obtain_response(rpc_connection=rpc_connection, request=request, raise_exception=raise_exception)
