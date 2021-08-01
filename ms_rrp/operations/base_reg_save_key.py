from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Union, Optional, cast
from struct import pack as struct_pack, unpack as struct_unpack
from pathlib import PureWindowsPath

from msdsalgs.win32_error import Win32ErrorCode
from msdsalgs.rpc.rpc_security_attributes import RPCSecurityAttributes
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.structures.pointer import Pointer, NullPointer
from ndr.utils import calculate_pad_length, pad as ndr_pad

from ms_rrp.operations import Operation
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString


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

        security_attributes_ndr_pointer = Pointer.from_bytes(data=data[20+calculate_pad_length(len(ndr_save_path)):])

        return cls(
            key_handle=data[:20],
            save_path=ndr_save_path.representation,
            security_attributes=(
                None if isinstance(security_attributes_ndr_pointer, NullPointer)
                else RPCSecurityAttributes.from_bytes(data=security_attributes_ndr_pointer.representation)
            )
        )

    # TODO: Does this really work? Don't I need a `Pointer`?
    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(bytes(RRPUnicodeString(representation=str(self.save_path)))),
            bytes(self.security_attributes) if self.security_attributes is not None else bytes(NullPointer())
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
