from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, cast

from msdsalgs.win32_error import Win32ErrorCode
from msdsalgs.rpc.rpc_security_attributes import RPCSecurityAttributes
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.structures.pointer import Pointer
from rpc.utils.types import DWORD

from ms_rrp.operations import Operation
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.rpc_hkey import RpcHkey


@dataclass
class BaseRegSaveKeyResponse(ClientProtocolResponseBase):
    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'return_code': (DWORD, Win32ErrorCode)
    }


@dataclass
class BaseRegSaveKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_SAVE_KEY

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
        'save_path': (RRPUnicodeString,),
        'security_attributes': (Pointer, RPCSecurityAttributes)
    }

    key_handle: bytes
    security_attributes: RPCSecurityAttributes = RPCSecurityAttributes()


BaseRegSaveKeyResponse.REQUEST_CLASS = BaseRegSaveKeyRequest
BaseRegSaveKeyRequest.RESPONSE_CLASS = BaseRegSaveKeyResponse


async def base_reg_save_key(
    rpc_connection: RPCConnection,
    request: BaseRegSaveKeyRequest,
    raise_exception: bool = True
) -> BaseRegSaveKeyResponse:
    """
    Perform the `BaseRegSaveKey` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/f022247d-6ef1-4f46-b195-7f60654f4a0d

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `BaseRegSaveKey` request.
    :param raise_exception: Whether to raise an exception in case the the response indicates an error occurred.
    :return: The `BaseRegSaveKey` response.
    """

    return cast(
        BaseRegSaveKeyResponse,
        await obtain_response(rpc_connection=rpc_connection, request=request, raise_exception=raise_exception)
    )
