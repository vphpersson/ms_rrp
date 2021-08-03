from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, ByteString, cast
from struct import Struct, calcsize

from msdsalgs.win32_error import Win32ErrorCode
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.structures.unidimensional_conformant_array import UnidimensionalConformantArray
from ndr.utils import calculate_pad_length, pad as ndr_pad
from rpc.connection import Connection as RPCConnection

from ms_rrp.operations import Operation
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.reg_value_type import RegValueType, REG_VALUE_TYPE_TO_STRUCT_FORMAT


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

    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')
    _VALUE_TYPE_STRUCT: ClassVar[Struct] = Struct('<I')
    _VALUE_LEN_STRUCT: ClassVar[Struct] = Struct('<I')

    key_handle: bytes
    sub_key_name: str
    value_type: RegValueType
    value: bytes

    # TODO: Consider default value for `strict` parameter.
    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0, strict: bool = False) -> BaseRegSetValueRequest:

        data = memoryview(data)[base_offset:]
        offset = 0

        key_handle: bytes = cls._KEY_HANDLE_STRUCT.unpack_from(buffer=data, offset=offset)[0]
        offset += cls._KEY_HANDLE_STRUCT.size

        ndr_sub_key_name = RRPUnicodeString.from_bytes(data[offset:])
        offset += calculate_pad_length(length_unpadded=len(ndr_sub_key_name))

        value_type = RegValueType(cls._VALUE_TYPE_STRUCT.unpack_from(buffer=data, offset=offset)[0])
        offset += cls._VALUE_TYPE_STRUCT.size

        ndr_value = UnidimensionalConformantArray.from_bytes(
            data=bytes(
                data[
                    offset
                    :
                    offset+UnidimensionalConformantArray.STRUCTURE_SIZE+calcsize(REG_VALUE_TYPE_TO_STRUCT_FORMAT[value_type])
                ]
            )
        )
        offset += len(ndr_value)

        value_len: int = cls._VALUE_LEN_STRUCT.unpack_from(buffer=data, offset=offset)[0]
        # TODO: Check if correct?

        return cls(
            key_handle=key_handle,
            sub_key_name=ndr_sub_key_name.representation,
            value_type=value_type,
            value=b''.join(ndr_value.representation)
        )

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(bytes(RRPUnicodeString(representation=self.sub_key_name))),
            self._VALUE_TYPE_STRUCT.pack(self.value_type.value),
            bytes(UnidimensionalConformantArray(tuple(self.value))),
            self._VALUE_LEN_STRUCT.pack(len(self.value))
        ])


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
