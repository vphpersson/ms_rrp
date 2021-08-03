from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, ByteString, AsyncIterator, cast
from struct import Struct
from enum import IntEnum
from contextlib import asynccontextmanager

from msdsalgs.win32_error import Win32ErrorCode
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.structures.pointer import Pointer
from ndr.utils import pad as ndr_pad, calculate_pad_length
from rpc.connection import Connection as RPCConnection
from msdsalgs.rpc.rpc_security_attributes import RPCSecurityAttributes

from ms_rrp.operations import Operation
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.reg_options import RegOptions
from ms_rrp.structures.regsam import Regsam
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


class Disposition(IntEnum):
    REG_CREATED_NEW_KEY = 1
    REG_OPENED_EXISTING_KEY = 2


@dataclass
class BaseRegCreateKeyResponse(ClientProtocolResponseBase):
    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')
    _DISPOSITION_STRUCT: ClassVar[Struct] = Struct('<I')

    key_handle: bytes
    disposition: Disposition

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegCreateKeyResponse:
        data = memoryview(data)[base_offset:]
        offset = 0

        key_handle: bytes = cls._KEY_HANDLE_STRUCT.unpack_from(buffer=data, offset=offset)[0]
        offset += cls._KEY_HANDLE_STRUCT.size

        disposition = Disposition(
            cls._DISPOSITION_STRUCT.unpack_from(
                Pointer.from_bytes(data=data, base_offset=offset).representation
            )[0]
        )
        offset += Pointer.structure_size + cls._DISPOSITION_STRUCT.size

        return_code = Win32ErrorCode(cls._RETURN_CODE_STRUCT.unpack_from(buffer=data, offset=offset)[0])

        return cls(
            key_handle=key_handle,
            disposition=disposition,
            return_code=return_code
        )

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            bytes(Pointer(representation=self._DISPOSITION_STRUCT.pack(self.disposition))),
            self._RETURN_CODE_STRUCT.pack(self.return_code)
        ])


@dataclass
class BaseRegCreateKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_CREATE_KEY

    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')
    _OPTIONS_STRUCT: ClassVar[Struct] = Struct('<I')
    _SAM_DESIRED_STRUCT: ClassVar[Struct] = Struct('<I')
    _DISPOSITION_STRUCT: ClassVar[Struct] = Struct('<I')

    key_handle: bytes
    sub_key_name: str
    class_name: str = ''
    options: RegOptions = RegOptions()
    sam_desired: Regsam = Regsam()
    security_attributes: RPCSecurityAttributes = RPCSecurityAttributes()
    disposition: Disposition = Disposition.REG_CREATED_NEW_KEY

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0, strict: bool = False) -> BaseRegCreateKeyRequest:

        data = memoryview(data)[base_offset:]
        offset = 0

        key_handle: bytes = cls._KEY_HANDLE_STRUCT.unpack_from(buffer=data, offset=offset)[0]
        offset += cls._KEY_HANDLE_STRUCT.size

        ndr_sub_key_name = RRPUnicodeString.from_bytes(data=data[offset:])
        offset += calculate_pad_length(len(ndr_sub_key_name))

        ndr_class_name = RRPUnicodeString.from_bytes(data=data[offset:])
        offset += calculate_pad_length(len(ndr_class_name))

        options = RegOptions.from_int(value=cls._OPTIONS_STRUCT.unpack_from(buffer=data, offset=offset)[0])
        offset += cls._OPTIONS_STRUCT.size

        sam_desired = Regsam.from_int(value=cls._SAM_DESIRED_STRUCT.unpack_from(buffer=data, offset=offset)[0])
        offset += cls._SAM_DESIRED_STRUCT.size

        security_attributes_pointer = Pointer.from_bytes(data=data, base_offset=offset)
        offset += Pointer.structure_size
        security_attributes = RPCSecurityAttributes.from_bytes(data=security_attributes_pointer.representation)
        offset += calculate_pad_length(len(security_attributes))

        disposition_pointer = Pointer.from_bytes(data=data, base_offset=offset)
        offset += Pointer.structure_size
        disposition = Disposition(cls._DISPOSITION_STRUCT.unpack_from(buffer=disposition_pointer.representation)[0])

        return cls(
            key_handle=key_handle,
            sub_key_name=ndr_sub_key_name.representation,
            class_name=ndr_class_name.representation,
            options=options,
            sam_desired=sam_desired,
            security_attributes=security_attributes,
            disposition=disposition
        )

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(bytes(RRPUnicodeString(representation=self.sub_key_name))),
            ndr_pad(bytes(RRPUnicodeString(representation=self.class_name))),
            self._OPTIONS_STRUCT.pack(int(self.options)),
            self._SAM_DESIRED_STRUCT.pack(int(self.sam_desired)),
            ndr_pad(bytes(Pointer(representation=bytes(self.security_attributes)))),
            bytes(Pointer(representation=self._DISPOSITION_STRUCT.pack(self.disposition)))
        ])


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
