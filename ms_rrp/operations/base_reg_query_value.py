from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, cast

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from rpc.utils.types import LPDWORD, DWORD, LPBYTE_VAR

from ms_rrp.operations import Operation
from ms_rrp.structures.reg_value_type import RegValueType
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.rpc_hkey import RpcHkey


@dataclass
class BaseRegQueryValueResponse(ClientProtocolResponseBase):
    # TODO: Add `parsed_value` property.

    value_type: RegValueType
    value: bytes

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'value_type': (LPDWORD, RegValueType),
        'value': (LPBYTE_VAR,),
        '__data_len': (LPDWORD,),
        '__data_size': (LPDWORD,),
        'return_code': (DWORD, Win32ErrorCode)
    }

    @property
    def data_len(self) -> int:
        return len(self.value)

    @property
    def data_size(self) -> int:
        return len(self.value)


@dataclass
class BaseRegQueryValueRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_QUERY_VALUE

    key_handle: bytes
    value_name: str
    value_buffer_size: int = 32
    value_type: RegValueType = RegValueType.REG_NONE

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
        'value_name': (RRPUnicodeString,),
        'value_type': (LPDWORD, RegValueType),
        '__data': (LPBYTE_VAR,),
        '__data_len': (LPDWORD,),
        '__data_size': (LPDWORD,)
    }

    @property
    def data(self) -> bytes:
        return bytes(self.value_buffer_size)

    @property
    def data_len(self) -> int:
        return self.value_buffer_size

    @property
    def data_size(self) -> int:
        return self.value_buffer_size


BaseRegQueryValueResponse.REQUEST_CLASS = BaseRegQueryValueRequest
BaseRegQueryValueRequest.RESPONSE_CLASS = BaseRegQueryValueResponse


async def base_reg_query_value(
    rpc_connection: RPCConnection,
    request: BaseRegQueryValueRequest,
    raise_exception: bool = True
) -> BaseRegQueryValueResponse:
    """
    Perform the `BaseRegQueryValue` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/8bc10aa3-2f91-44e8-aa33-b3263c49ab9d

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `BaseRegSaveKey` request.
    :param raise_exception: Whether to raise an exception in case the the response indicates an error occurred.
    :return: The `BaseRegSaveKey` response.
    """

    return cast(
        BaseRegQueryValueResponse,
        await obtain_response(rpc_connection=rpc_connection, request=request, raise_exception=raise_exception)
    )
