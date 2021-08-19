from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, AsyncIterator, cast
from contextlib import asynccontextmanager

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from rpc.utils.types import DWORD

from ms_rrp.operations import Operation
from ms_rrp.structures.rpc_hkey import RpcHkey
from ms_rrp.structures.regsam import Regsam
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.reg_options import RegOptions
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


@dataclass
class BaseRegOpenKeyResponse(ClientProtocolResponseBase):
    key_handle: bytes

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
        'return_code': (DWORD, Win32ErrorCode)
    }


@dataclass
class BaseRegOpenKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_OPEN_KEY

    key_handle: bytes
    sub_key_name: str
    options: RegOptions = RegOptions()
    sam_desired: Regsam = Regsam(maximum_allowed=True)

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
        'sub_key_name': (RRPUnicodeString,),
        'options': (DWORD, RegOptions.from_int),
        'sam_desired': (DWORD, Regsam.from_int)
    }


BaseRegOpenKeyResponse.REQUEST_CLASS = BaseRegOpenKeyRequest
BaseRegOpenKeyRequest.RESPONSE_CLASS = BaseRegOpenKeyResponse


@asynccontextmanager
async def base_reg_open_key(
    rpc_connection: RPCConnection,
    request: BaseRegOpenKeyRequest,
    raise_exception: bool = True
) -> AsyncIterator[BaseRegOpenKeyResponse]:
    """
    Perform the `BaseRegOpenKey` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/8cb48f55-19e1-4ea2-8d76-dd0f6934f0d9

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `BaseRegOpenKey` request.
    :param raise_exception: Whether to raise an exception in case the response indicates an error occurred.
    :return: The `BaseRegOpenKey` response.
    """

    base_reg_open_key_response = cast(
        BaseRegOpenKeyResponse,
        await obtain_response(
            rpc_connection=rpc_connection,
            request=request,
            raise_exception=raise_exception
        )
    )

    yield base_reg_open_key_response

    await base_reg_close_key(
        rpc_connection=rpc_connection,
        request=BaseRegCloseKeyRequest(
            key_handle=base_reg_open_key_response.key_handle
        )
    )
