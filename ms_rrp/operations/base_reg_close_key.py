from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, cast

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response

from ms_rrp.operations import Operation
from ms_rrp.structures.rpc_hkey import RpcHkey
from rpc.utils.types import DWORD


@dataclass
class BaseRegCloseKeyResponse(ClientProtocolResponseBase):
    key_handle: bytes

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
        'return_code': (DWORD, Win32ErrorCode)
    }


@dataclass
class BaseRegCloseKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_CLOSE_KEY

    key_handle: bytes

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
    }


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
