from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, AsyncIterator, cast
from contextlib import asynccontextmanager

from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import obtain_response

from ms_rrp.operations import Operation, OpenRootKeyRequest, OpenRootKeyResponse
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


@dataclass
class OpenUsersResponse(OpenRootKeyResponse):
    pass


@dataclass
class OpenUsersRequest(OpenRootKeyRequest):
    OPERATION: ClassVar[Operation] = Operation.OPEN_USERS


OpenUsersResponse.REQUEST_CLASS = OpenUsersRequest
OpenUsersRequest.RESPONSE_CLASS = OpenUsersResponse


@asynccontextmanager
async def open_users(
    rpc_connection: RPCConnection,
    request: OpenUsersRequest,
    raise_exception: bool = True
) -> AsyncIterator[OpenUsersResponse]:
    """
    Perform the `OpenUsers` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/6cef29ae-21ba-423f-9158-05145ac80a5b

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `OpenUsers` request.
    :param raise_exception: Whether to raise an exception in case the response indicates an error occurred.
    :return: The `OpenUsers` response.
    """

    open_users_response = cast(
        OpenUsersResponse,
        await obtain_response(
            rpc_connection=rpc_connection,
            request=request,
            raise_exception=raise_exception
        )
    )

    yield open_users_response

    await base_reg_close_key(
        rpc_connection=rpc_connection,
        request=BaseRegCloseKeyRequest(
            key_handle=open_users_response.key_handle
        )
    )
