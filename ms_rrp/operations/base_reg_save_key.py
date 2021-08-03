from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Union, cast, ByteString
from struct import Struct
from pathlib import PureWindowsPath

from msdsalgs.win32_error import Win32ErrorCode
from msdsalgs.rpc.rpc_security_attributes import RPCSecurityAttributes
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.structures.pointer import Pointer
from ndr.utils import calculate_pad_length, pad as ndr_pad

from ms_rrp.operations import Operation
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString


@dataclass
class BaseRegSaveKeyResponse(ClientProtocolResponseBase):

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegSaveKeyResponse:
        return cls(return_code=Win32ErrorCode(cls._RETURN_CODE_STRUCT.unpack_from(buffer=data, offset=base_offset)[0]))

    def __bytes__(self) -> bytes:
        return self._RETURN_CODE_STRUCT.pack(self.return_code)

    def __len__(self) -> int:
        return self._RETURN_CODE_STRUCT.size


@dataclass
class BaseRegSaveKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_SAVE_KEY

    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')

    key_handle: bytes
    save_path: Union[str, PureWindowsPath]
    security_attributes: RPCSecurityAttributes

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegSaveKeyRequest:
        data = memoryview(data)[base_offset:]
        offset = 0

        key_handle: bytes = cls._KEY_HANDLE_STRUCT.unpack_from(buffer=data, offset=base_offset)[0]
        offset += cls._KEY_HANDLE_STRUCT.size

        ndr_save_path = RRPUnicodeString.from_bytes(data=data, base_offset=offset)
        offset += calculate_pad_length(length_unpadded=len(ndr_save_path))

        security_attributes_ndr_pointer = Pointer.from_bytes(data=data, base_offset=offset)
        offset += Pointer.structure_size
        security_attributes = RPCSecurityAttributes.from_bytes(data=security_attributes_ndr_pointer.representation)
        offset += calculate_pad_length(length_unpadded=len(security_attributes))

        return cls(
            key_handle=key_handle,
            save_path=ndr_save_path.representation,
            security_attributes=security_attributes
        )

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(bytes(RRPUnicodeString(representation=str(self.save_path)))),
            bytes(Pointer(representation=bytes(self.security_attributes)))
        ])


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
