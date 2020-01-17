from __future__ import annotations
from dataclasses import dataclass
from abc import ABC
from typing import ClassVar, Union, Optional
from enum import Enum
from struct import pack as struct_pack, unpack as struct_unpack
from pathlib import PureWindowsPath

from msdsalgs.win32_error import Win32ErrorCode
from msdsalgs.security_types.security_descriptor import SecurityDescriptor
from rpc.connection import Connection as RPCConnection
from rpc.ndr import ConformantVaryingString, Pointer, NullPointer
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from rpc.utils.ndr import calculate_pad_length

from ms_rrp.operations import Operation


@dataclass
class RPCUnicodeString:
    representation: str

    @classmethod
    def from_bytes(cls, data: bytes) -> RPCUnicodeString:
        length: int = struct_unpack('<H', data[:2])[0]
        maximum_length: int = struct_unpack('<H', data[2:4])[0]

        ndr_string = ConformantVaryingString.from_bytes(
            data=data[4+Pointer.structure_size:4+Pointer.structure_size+maximum_length]
        )

        return cls(representation=ndr_string.representation)

    def __bytes__(self) -> bytes:
        ndr_pointer_bytes = bytes(Pointer(representation=ConformantVaryingString(representation=self.representation)))

        return b''.join([
            struct_pack('<H', len(ndr_pointer_bytes)),
            struct_pack('<H', len(ndr_pointer_bytes)),
            ndr_pointer_bytes
        ])


@dataclass
class RRPUnicodeString(RPCUnicodeString):

    @classmethod
    def from_bytes(cls, data: bytes) -> RRPUnicodeString:
        rpc_unicode_string: RPCUnicodeString = RPCUnicodeString.from_bytes(data=data)
        # TODO: Wrong. Should only remove one null character.
        return cls(representation=rpc_unicode_string.representation.rstrip('\x00'))

    # def __bytes__(self) -> bytes:
    #     self.representation += '\x00'
    #     bytes_value = super().__bytes__()
    #     self.representation = self.representation[:-1]
    #     return bytes_value

    def __len__(self) -> int:
        return len(self.__bytes__())


@dataclass
class RPCSecurityDescriptor:
    STRUCTURE_SIZE: ClassVar[int] = 8

    security_descriptor: SecurityDescriptor

    @property
    def in_security_descriptor(self) -> int:
        # TODO: Use `__len__` method once added.
        return len(bytes(self.security_descriptor))

    @property
    def out_security_descriptor(self) -> int:
        return len(bytes(self.security_descriptor))

    @classmethod
    def from_bytes(cls, data: bytes) -> RPCSecurityDescriptor:
        return cls(security_descriptor=SecurityDescriptor.from_bytes(data=data))

    def __bytes__(self) -> bytes:
        return b''.join([
            bytes(self.security_descriptor),
            struct_pack('<H', self.in_security_descriptor),
            struct_pack('<H', self.out_security_descriptor)
        ])

    def __len__(self) -> int:
        return len(self.__bytes__())


@dataclass
class RPCSecurityAttributes:
    rpc_security_descriptor: RPCSecurityDescriptor
    inherit_handle: bool

    @classmethod
    def from_bytes(cls, data: bytes) -> RPCSecurityAttributes:
        rpc_security_descriptor = RPCSecurityDescriptor.from_bytes(data=data)
        return cls(
            rpc_security_descriptor=rpc_security_descriptor,
            inherit_handle=bool(data[len(rpc_security_descriptor)])
        )


@dataclass
class BaseRegSaveKeyResponse(ClientProtocolResponseBase):

    @classmethod
    def from_bytes(cls, data: bytes) -> BaseRegSaveKeyResponse:
        return cls(return_code=Win32ErrorCode(struct_unpack('<I', data[:4])[0]))

    def __bytes__(self) -> bytes:
        return struct_pack('<I', self.return_code)


@dataclass
class BaseRegSaveKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_SAVE_KEY

    key_handle: bytes
    save_path: Union[str, PureWindowsPath]
    security_attributes: Optional[RPCSecurityAttributes] = None

    @classmethod
    def from_bytes(cls, data: bytes) -> BaseRegSaveKeyRequest:

        ndr_save_path = RRPUnicodeString.from_bytes(data[20:])

        m = RPCUnicodeString.from_bytes(data=bytes(ndr_save_path))

        security_attributes_ndr_pointer = Pointer.from_bytes(data=data[20+calculate_pad_length(len(ndr_save_path)):])

        return cls(
            key_handle=data[:20],
            save_path=ndr_save_path.representation,
            security_attributes=(
                None if isinstance(security_attributes_ndr_pointer, NullPointer)
                else RPCSecurityAttributes.from_bytes(data=security_attributes_ndr_pointer.representation)
            )
        )

    def __bytes__(self) -> bytes:
        return ...


BaseRegSaveKeyResponse.REQUEST_CLASS = BaseRegSaveKeyRequest
BaseRegSaveKeyRequest.RESPONSE_CLASS = BaseRegSaveKeyResponse


async def base_reg_save_key(
    rpc_connection: RPCConnection,
    request: BaseRegSaveKeyRequest,
    raise_exception: bool = True
) -> BaseRegSaveKeyResponse:
    """
    Perform the BaseRegSaveKey operation.

    :param rpc_connection:
    :param request:
    :param raise_exception:
    :return:
    """

    return await obtain_response(rpc_connection=rpc_connection, request=request, raise_exception=raise_exception)


a = BaseRegSaveKeyRequest.from_bytes(
    data=bytes.fromhex('0000000087ef65b732d2f74b966c16d46c4590dd6a006a00fab3000035000000000000003500000043003a005c00570069006e0064006f00770073005c00540065006d0070005c00350035003900380065003900310065002d0064003700380038002d0034003800640062002d0062006400390036002d003100340062006500370036006400640032003700610034000000bfbf00000000')
)
b = 1
