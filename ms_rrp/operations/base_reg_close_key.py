from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, cast
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
    Perform the `BaseRegCloseKey` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/bc7545ff-0a54-4465-a95a-396b5c2995df

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `BaseRegCloseKey` request.
    :param raise_exception: Whether to raise an exception in case the response indicates an error occurred.
    :return: The `BaseRegCloseKey` response.
    """

    return cast(
        BaseRegCloseKeyResponse,
        await obtain_response(rpc_connection=rpc_connection, request=request, raise_exception=raise_exception)
    )
