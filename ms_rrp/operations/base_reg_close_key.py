from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, cast, ByteString
from struct import Struct

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response

from ms_rrp.operations import Operation


@dataclass
class BaseRegCloseKeyResponse(ClientProtocolResponseBase):
    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')

    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegCloseKeyResponse:
        data = memoryview(data)[base_offset:]
        offset = 0

        key_handle: bytes = cls._KEY_HANDLE_STRUCT.unpack_from(buffer=data, offset=offset)[0]
        offset += cls._KEY_HANDLE_STRUCT.size

        return_code = Win32ErrorCode(cls._RETURN_CODE_STRUCT.unpack_from(buffer=data, offset=offset)[0])
        offset += cls._RETURN_CODE_STRUCT.size

        return cls(key_handle=key_handle, return_code=return_code)

    def __bytes__(self) -> bytes:
        return self.key_handle + self._RETURN_CODE_STRUCT.pack(self.return_code)

    def __len__(self) -> int:
        return self._KEY_HANDLE_STRUCT.size + self._RETURN_CODE_STRUCT.size


@dataclass
class BaseRegCloseKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_CLOSE_KEY
    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')

    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegCloseKeyRequest:
        return cls(key_handle=cls._KEY_HANDLE_STRUCT.unpack_from(buffer=data, offset=base_offset)[0])

    def __bytes__(self) -> bytes:
        return self.key_handle

    def __len__(self) -> int:
        return self._KEY_HANDLE_STRUCT.size


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
