from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, ByteString, AsyncIterator, cast
from contextlib import asynccontextmanager

from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import obtain_response

from ms_rrp.operations import Operation, OpenRootKeyRequest, OpenRootKeyResponse
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


@dataclass
class OpenClassesRootResponse(OpenRootKeyResponse):
    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> OpenClassesRootResponse:
        return cast(
            OpenClassesRootResponse,
            super().from_bytes(data=data, base_offset=base_offset)
        )


@dataclass
class OpenClassesRootRequest(OpenRootKeyRequest):
    OPERATION: ClassVar[Operation] = Operation.OPEN_CLASSES_ROOT

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> OpenClassesRootRequest:
        return cast(
            OpenClassesRootRequest,
            super().from_bytes(data=data, base_offset=base_offset)
        )



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
