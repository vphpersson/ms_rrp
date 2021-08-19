from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, ByteString, cast, Type
from struct import Struct

from msdsalgs.win32_error import Win32ErrorCode
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from rpc.connection import Connection as RPCConnection
from rpc.utils.types import DWORD, BYTE_ARRAY

from ms_rrp.operations import Operation
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.reg_value_type import RegValueType
from ms_rrp.structures.rpc_hkey import RpcHkey


@dataclass
class BaseRegSetValueResponse(ClientProtocolResponseBase):

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegSetValueResponse:
        return cls(return_code=Win32ErrorCode(cls._RETURN_CODE_STRUCT.unpack_from(buffer=data, offset=base_offset)[0]))

    def __bytes__(self) -> bytes:
        return self._RETURN_CODE_STRUCT.pack(self.return_code)

    def __len__(self) -> int:
        return self._RETURN_CODE_STRUCT.size


@dataclass
class BaseRegSetValueRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_SET_VALUE

    key_handle: bytes
    sub_key_name: str
    value_type: RegValueType
    value: bytes

    _STRUCTURE: ClassVar[dict[str, tuple[Type, ...]]] = {
        'key_handle': (RpcHkey,),
        'sub_key_name': (RRPUnicodeString,),
        'value_type': (DWORD, RegValueType),
        'value': (BYTE_ARRAY,),
        '__value_len': (DWORD,)
    }

    @property
    def value_len(self):
        return len(self.value)


BaseRegSetValueResponse.REQUEST_CLASS = BaseRegSetValueRequest
BaseRegSetValueRequest.RESPONSE_CLASS = BaseRegSetValueResponse


async def base_reg_set_value(
    rpc_connection: RPCConnection,
    request: BaseRegSetValueRequest,
    raise_exception: bool = True
) -> BaseRegSetValueResponse:
    """
    Perform the `BaseRegSetValue` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/2b61fa7e-2a38-46ce-a186-7c91b3ed1b61

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `BaseRegSetValue` request.
    :param raise_exception: Whether to raise an exception in case the response indicates an error occurred.
    :return: A `BaseRegSetValue` response.
    """

    return cast(
        BaseRegSetValueResponse,
        await obtain_response(rpc_connection=rpc_connection, request=request, raise_exception=raise_exception)
    )
