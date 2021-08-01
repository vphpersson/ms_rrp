from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, ByteString, AsyncIterator, cast
from struct import pack, unpack_from
from contextlib import asynccontextmanager

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response

from ms_rrp.operations import Operation
from ms_rrp.structures.regsam import Regsam
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


@dataclass
class OpenClassesRootResponse(ClientProtocolResponseBase):
    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> OpenClassesRootResponse:
        return cls(
            key_handle=data[:20],
            return_code=Win32ErrorCode(unpack_from('<I', buffer=data, offset=base_offset+20)[0])
        )

    def __bytes__(self) -> bytes:
        return self.key_handle + pack('<I', self.return_code)


@dataclass
class OpenClassesRootRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.OPEN_CLASSES_ROOT
    _RESERVED_SERVER_NAME: ClassVar[bytes] = bytes(4)

    sam_desired: Regsam

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> OpenClassesRootRequest:
        # TODO: Check reserved `ServerName` if `strict` is set?
        return cls(sam_desired=Regsam.from_int(unpack_from('<I', buffer=data, offset=base_offset+4)[0]))

    def __bytes__(self) -> bytes:
        return self._RESERVED_SERVER_NAME + pack('<I', int(self.sam_desired))


OpenClassesRootResponse.REQUEST_CLASS = OpenClassesRootRequest
OpenClassesRootRequest.RESPONSE_CLASS = OpenClassesRootResponse


@asynccontextmanager
async def open_classes_root(
    rpc_connection: RPCConnection,
    request: OpenClassesRootRequest,
    raise_exception: bool = True
) -> AsyncIterator[OpenClassesRootResponse]:
    """
    Perform the `OpenClassesRoot` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/956a3052-6580-43ee-91aa-aaf61726149b

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `OpenClassesRoot` request.
    :param raise_exception: Whether to raise an exception in case the response indicates an error occurred.
    :return: The `OpenClassesRoot` response.
    """

    open_classes_root_response = cast(
        OpenClassesRootResponse,
        await obtain_response(
            rpc_connection=rpc_connection,
            request=request,
            raise_exception=raise_exception
        )
    )

    yield open_classes_root_response

    await base_reg_close_key(
        rpc_connection=rpc_connection,
        request=BaseRegCloseKeyRequest(key_handle=open_classes_root_response.key_handle)
    )
