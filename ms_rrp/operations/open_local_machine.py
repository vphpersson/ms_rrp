from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, AsyncIterator, cast, ByteString
from struct import Struct
from contextlib import asynccontextmanager

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response

from ms_rrp.operations import Operation
from ms_rrp.structures.regsam import Regsam
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


@dataclass
class OpenLocalMachineResponse(ClientProtocolResponseBase):
    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')

    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> OpenLocalMachineResponse:
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
class OpenLocalMachineRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.OPEN_LOCAL_MACHINE
    _RESERVED_SERVER_NAME: ClassVar[bytes] = bytes(4)

    _SAM_DESIRED_STRUCT: ClassVar[Struct] = Struct('<I')

    sam_desired: Regsam

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> OpenLocalMachineRequest:
        data = memoryview(data)[base_offset:]
        offset = 0

        # TODO: Check reserved `ServerName` if `strict` is set?
        offset += 4

        return cls(sam_desired=Regsam.from_int(cls._SAM_DESIRED_STRUCT.unpack_from(buffer=data, offset=offset)[0]))

    def __bytes__(self) -> bytes:
        return self._RESERVED_SERVER_NAME + self._SAM_DESIRED_STRUCT.pack(int(self.sam_desired))

    def __len__(self) -> int:
        return len(self._RESERVED_SERVER_NAME) + self._SAM_DESIRED_STRUCT.size


OpenLocalMachineResponse.REQUEST_CLASS = OpenLocalMachineRequest
OpenLocalMachineRequest.RESPONSE_CLASS = OpenLocalMachineResponse


@asynccontextmanager
async def open_local_machine(
    rpc_connection: RPCConnection,
    request: OpenLocalMachineRequest,
    raise_exception: bool = True
) -> AsyncIterator[OpenLocalMachineResponse]:
    """
    Perform the `OpenLocalMachine` operation.

    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rrp/6cef29ae-21ba-423f-9158-05145ac80a5b

    :param rpc_connection: An RPC connection with which to perform the operation.
    :param request: The `OpenLocalMachine` request.
    :param raise_exception: Whether to raise an exception in case the response indicates an error occurred.
    :return: The `OpenLocalMachine` response.
    """

    open_local_machine_response = cast(
        OpenLocalMachineResponse,
        await obtain_response(
            rpc_connection=rpc_connection,
            request=request,
            raise_exception=raise_exception
        )
    )

    yield open_local_machine_response

    await base_reg_close_key(
        rpc_connection=rpc_connection,
        request=BaseRegCloseKeyRequest(
            key_handle=open_local_machine_response.key_handle
        )
    )
