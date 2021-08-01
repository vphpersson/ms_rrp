from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, ByteString, cast
from struct import pack, unpack_from

from msdsalgs.win32_error import Win32ErrorCode
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.structures.unidimensional_conformant_array import UnidimensionalConformantArray
from ndr.utils import calculate_pad_length, pad as ndr_pad
from rpc.connection import Connection as RPCConnection

from ms_rrp.operations import Operation
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.reg_value_type import RegValueType


@dataclass
class BaseRegSetValueResponse(ClientProtocolResponseBase):

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegSetValueResponse:
        return cls(return_code=Win32ErrorCode(unpack_from('<I', buffer=data, offset=base_offset)[0]))

    def __bytes__(self) -> bytes:
        return pack('<I', self.return_code)


@dataclass
class BaseRegSetValueRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_SET_VALUE

    key_handle: bytes
    sub_key_name: str
    value_type: RegValueType
    value: bytes

    # TODO: Consider default value for `strict` parameter.
    # TODO: Test
    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0, strict: bool = False):

        offset: int = base_offset
        data = memoryview(data)[offset:]

        key_handle = bytes(data[:20])
        offset += 20

        ndr_sub_key_name = RRPUnicodeString.from_bytes(data[offset:])
        offset += calculate_pad_length(len(ndr_sub_key_name))

        value_type = RegValueType(unpack_from('<I', buffer=data, offset=offset)[0])
        offset += 4

        ndr_array = UnidimensionalConformantArray.from_bytes(data=bytes(data[offset:len(data)-4]))

        value_len: int = unpack_from('<I', buffer=data, offset=len(data)-4)[0]
        # TODO: Check if correct?

        return cls(
            key_handle=key_handle,
            sub_key_name=ndr_sub_key_name.representation,
            value_type=value_type,
            value=b''.join(ndr_array.representation)
        )

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(bytes(RRPUnicodeString(representation=self.sub_key_name))),
            pack('<I', self.value_type.value),
            bytes(UnidimensionalConformantArray(tuple(self.value))),
            pack('<I', len(self.value))
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
