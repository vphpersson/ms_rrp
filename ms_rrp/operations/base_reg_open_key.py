from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, AsyncIterator, cast, ByteString
from struct import Struct
from contextlib import asynccontextmanager

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from ndr.utils import calculate_pad_length, pad as ndr_pad

from ms_rrp.operations import Operation
from ms_rrp.structures.regsam import Regsam
from ms_rrp.structures.rrp_unicode_string import RRPUnicodeString
from ms_rrp.structures.reg_options import RegOptions
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


@dataclass
class BaseRegOpenKeyResponse(ClientProtocolResponseBase):
    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')

    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegOpenKeyResponse:
        data = memoryview(data)[base_offset:]
        offset = 0

        key_handle: bytes = cls._KEY_HANDLE_STRUCT.unpack_from(buffer=data, offset=offset)[0]
        offset += cls._KEY_HANDLE_STRUCT.size

        return_code = Win32ErrorCode(cls._RETURN_CODE_STRUCT.unpack_from(buffer=data, offset=offset)[0])

        return cls(key_handle=key_handle, return_code=return_code)

    def __bytes__(self) -> bytes:
        return self.key_handle + self._RETURN_CODE_STRUCT.pack(self.return_code)

    def __len__(self) -> int:
        return self._KEY_HANDLE_STRUCT.size + self._RETURN_CODE_STRUCT.size


@dataclass
class BaseRegOpenKeyRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.BASE_REG_OPEN_KEY

    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')
    _OPTIONS_STRUCT: ClassVar[Struct] = Struct('<I')
    _SAM_DESIRED_STRUCT: ClassVar[Struct] = Struct('<I')

    key_handle: bytes
    sub_key_name: str
    options: RegOptions = RegOptions()
    sam_desired: Regsam = Regsam(maximum_allowed=True)

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> BaseRegOpenKeyRequest:
        data = memoryview(data)[base_offset:]
        offset = 0

        key_handle: bytes = cls._KEY_HANDLE_STRUCT.unpack_from(buffer=data, offset=offset)[0]
        offset += cls._KEY_HANDLE_STRUCT.size

        ndr_sub_key_name = RRPUnicodeString.from_bytes(data=data, base_offset=offset)
        offset += calculate_pad_length(len(ndr_sub_key_name))

        options = RegOptions.from_int(value=cls._OPTIONS_STRUCT.unpack_from(buffer=data, offset=offset)[0])
        offset += cls._OPTIONS_STRUCT.size

        sam_desired = Regsam.from_int(value=cls._SAM_DESIRED_STRUCT.unpack_from(buffer=data, offset=offset)[0])

        return cls(
            key_handle=key_handle,
            sub_key_name=ndr_sub_key_name.representation,
            options=options,
            sam_desired=sam_desired
        )

    def __bytes__(self) -> bytes:
        return b''.join([
            self.key_handle,
            ndr_pad(bytes(RRPUnicodeString(representation=self.sub_key_name))),
            self._OPTIONS_STRUCT.pack(int(self.options)),
            self._SAM_DESIRED_STRUCT.pack(int(self.sam_desired))
        ])


BaseRegOpenKeyResponse.REQUEST_CLASS = BaseRegOpenKeyRequest
BaseRegOpenKeyRequest.RESPONSE_CLASS = BaseRegOpenKeyResponse


@asynccontextmanager
async def base_reg_open_key(
    rpc_connection: RPCConnection,
    request: BaseRegOpenKeyRequest,
    raise_exception: bool = True
) -> AsyncIterator[BaseRegOpenKeyResponse]:
    """
    Perform the `BaseRegOpenKey` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/8cb48f55-19e1-4ea2-8d76-dd0f6934f0d9

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `BaseRegOpenKey` request.
    :param raise_exception: Whether to raise an exception in case the response indicates an error occurred.
    :return: The `BaseRegOpenKey` response.
    """

    base_reg_open_key_response = cast(
        BaseRegOpenKeyResponse,
        await obtain_response(
            rpc_connection=rpc_connection,
            request=request,
            raise_exception=raise_exception
        )
    )

    yield base_reg_open_key_response

    await base_reg_close_key(
        rpc_connection=rpc_connection,
        request=BaseRegCloseKeyRequest(
            key_handle=base_reg_open_key_response.key_handle
        )
    )
