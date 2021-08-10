from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Union, cast, ByteString, Optional
from struct import Struct
from pathlib import PureWindowsPath

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.structures.pointer import Pointer
from ndr.utils import calculate_pad_length, pad as ndr_pad
from ndr.structures.unidimensional_conformant_varying_array import UnidimensionalConformantVaryingArray

from ms_rrp.operations import Operation
from ms_rrp.structures.reg_value_type import RegValueType
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString

from typing import Annotated
from ctypes import c_ulong

DWORD = Annotated[c_ulong, int]
BYTE_ARRAY = UnidimensionalConformantVaryingArray
LPBYTE = Annotated[Pointer, BYTE_ARRAY]
LPDWORD = Annotated[Pointer, DWORD]


@dataclass
class BaseRegQueryValueResponse(ClientProtocolResponseBase):

    _VALUE_TYPE_STRUCT = Struct('<I')
    _DATA_LEN_STRUCT = Struct('<I')
    _DATA_SIZE_STRUCT = Struct('<I')

    _STRUCTURE = (
        (Pointer, Struct('<I'), RegValueType),
        (Pointer, UnidimensionalConformantVaryingArray),
        (Pointer, Struct('<I')),
        (Pointer, Struct('<I')),
        (Struct('<I'), Win32ErrorCode)
    )

    # TODO: Add `parsed_value` property.

    value_type: RegValueType
    value: bytes

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegQueryValueResponse:
        data = memoryview(data)[base_offset:]
        offset = 0

        value_type_pointer = Pointer.from_bytes(data=data[offset:offset+Pointer.structure_size + cls._VALUE_TYPE_STRUCT.size])
        offset += Pointer.structure_size
        value_type = RegValueType(cls._VALUE_TYPE_STRUCT.unpack_from(buffer=value_type_pointer.representation)[0])
        offset += cls._VALUE_TYPE_STRUCT.size

        value_pointer = Pointer.from_bytes(data=data, base_offset=offset)
        offset += Pointer.structure_size
        value_arr = UnidimensionalConformantVaryingArray.from_bytes(data=value_pointer.representation)
        value = value_arr.representation
        offset += calculate_pad_length(length_unpadded=len(value_arr))

        data_len_pointer = Pointer.from_bytes(data=data, base_offset=offset)
        offset += Pointer.structure_size
        data_len = cls._DATA_LEN_STRUCT.unpack_from(buffer=data_len_pointer.representation)
        offset += cls._DATA_LEN_STRUCT.size

        data_size_pointer = Pointer.from_bytes(data=data, base_offset=offset)
        offset += Pointer.structure_size
        data_size = cls._DATA_SIZE_STRUCT.unpack_from(buffer=data_size_pointer.representation)
        offset += cls._DATA_SIZE_STRUCT.size

        return_code = Win32ErrorCode(cls._RETURN_CODE_STRUCT.unpack_from(buffer=data, offset=offset)[0])

        return cls(value_type=value_type, value=value, return_code=return_code)

    def __bytes__(self) -> bytes:
        return b''.join([
            ndr_pad(bytes(Pointer(representation=self._VALUE_TYPE_STRUCT.pack(self.value_type)))),
            ndr_pad(bytes(Pointer(representation=UnidimensionalConformantVaryingArray(representation=self.value)))),
            ndr_pad(bytes(Pointer(representation=self._DATA_LEN_STRUCT.pack(len(self.value))))),
            ndr_pad(bytes(Pointer(representation=self._DATA_SIZE_STRUCT.pack(len(self.value))))),
            self._RETURN_CODE_STRUCT.pack(self.return_code)
        ])


@dataclass
class BaseRegQueryValueRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_QUERY_VALUE

    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')
    _VALUE_TYPE_STRUCT: ClassVar[Struct] = Struct('<I')
    _DATA_SIZE_STRUCT: ClassVar[Struct] = Struct('<I')
    _DATA_LEN_STRUCT: ClassVar[Struct] = Struct('<I')

    key_handle: bytes
    value_name: str
    value_buffer_size: int = 32
    value_type: RegValueType = RegValueType.REG_NONE

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegQueryValueRequest:
        ...

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(data=bytes(RRPUnicodeString(representation=self.value_name))),
            ndr_pad(bytes(Pointer(representation=self._VALUE_TYPE_STRUCT.pack(self.value_type)))),
            ndr_pad(
                bytes(
                    Pointer(
                        representation=UnidimensionalConformantVaryingArray(
                            representation=bytes(self.value_buffer_size)
                        )
                    )
                )
            ),
            ndr_pad(bytes(Pointer(representation=self._DATA_SIZE_STRUCT.pack(self.value_buffer_size)))),
            ndr_pad(bytes(Pointer(representation=self._DATA_LEN_STRUCT.pack(self.value_buffer_size))))
        ])


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
