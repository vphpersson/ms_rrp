from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, ByteString, AsyncIterator, cast
from struct import pack, unpack_from
from enum import IntEnum
from contextlib import asynccontextmanager

from msdsalgs.win32_error import Win32ErrorCode
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.structures.pointer import Pointer
from ndr.utils import pad as ndr_pad
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
    key_handle: bytes
    disposition: Disposition

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegCreateKeyResponse:
        return cls(
            key_handle=data[base_offset:base_offset+20],
            disposition=Disposition(unpack_from('<I', Pointer.from_bytes(data=data[base_offset+20:base_offset+28]).representation)[0]),
            return_code=Win32ErrorCode(unpack_from('<I', buffer=data, offset=base_offset+28)[0])
        )

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            bytes(Pointer(representation=pack('<I', self.disposition))),
            pack('<I', self.return_code)]
        )


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

    # TODO: Implement.
    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0, strict: bool = False) -> BaseRegCreateKeyRequest:
        ...

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(bytes(RRPUnicodeString(representation=self.sub_key_name))),
            ndr_pad(bytes(RRPUnicodeString(representation=self.class_name))),
            pack('<I', int(self.options)),
            pack('<I', int(self.sam_desired)),
            bytes(Pointer(representation=bytes(self.security_attributes))),
            bytes(Pointer(representation=pack('<I', self.disposition)))
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
