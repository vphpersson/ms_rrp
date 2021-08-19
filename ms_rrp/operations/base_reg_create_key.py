from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, AsyncIterator, cast
from contextlib import asynccontextmanager

from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from rpc.utils.types import DWORD, LPDWORD
from ndr.structures.pointer import Pointer
from msdsalgs.win32_error import Win32ErrorCode
from msdsalgs.rpc.rpc_security_attributes import RPCSecurityAttributes

from ms_rrp.operations import Operation
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.reg_options import RegOptions
from ms_rrp.structures.regsam import Regsam
from ms_rrp.structures.rpc_hkey import RpcHkey
from ms_rrp.structures.disposition import Disposition


@dataclass
class BaseRegCreateKeyResponse(ClientProtocolResponseBase):
    key_handle: bytes
    disposition: Disposition

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
        'disposition': (LPDWORD, Disposition),
        'return_code': (DWORD, Win32ErrorCode)
    }


@dataclass
class BaseRegCreateKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_CREATE_KEY

    key_handle: bytes
    sub_key_name: str
    class_name: str = ''
    options: RegOptions = RegOptions()
    sam_desired: Regsam = Regsam()
    security_attributes: RPCSecurityAttributes = RPCSecurityAttributes()
    disposition: Disposition = Disposition.REG_CREATED_NEW_KEY

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
        'sub_key_name': (RRPUnicodeString,),
        'class_name': (RRPUnicodeString,),
        'options': (DWORD, RegOptions.from_int),
        'sam_desired': (DWORD, Regsam.from_int),
        'security_attributes': (Pointer, RPCSecurityAttributes),
        'disposition': (LPDWORD, Disposition)
    }


BaseRegCreateKeyResponse.REQUEST_CLASS = BaseRegCreateKeyRequest
BaseRegCreateKeyRequest.RESPONSE_CLASS = BaseRegCreateKeyResponse


@asynccontextmanager
async def base_reg_create_key(
    rpc_connection: RPCConnection,
    request: BaseRegCreateKeyRequest,
    raise_exception: bool = True
) -> AsyncIterator[BaseRegCreateKeyResponse]:
    """
    Perform the `BaseRegCreateKey` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/c7186ae2-1c82-45e9-933b-97d9873657e8

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `BaseRegCreateKey` request.
    :param raise_exception: Whether to raise an exception in case the response indicates an error occurred.
    :return: The `BaseRegCreateKey` response.
    """

    base_reg_create_key_response = cast(
        BaseRegCreateKeyResponse,
        await obtain_response(
            rpc_connection=rpc_connection,
            request=request,
            raise_exception=raise_exception
        )
    )

    yield base_reg_create_key_response

    await base_reg_close_key(
        rpc_connection=rpc_connection,
        request=BaseRegCloseKeyRequest(
            key_handle=base_reg_create_key_response.key_handle
        )
    )
