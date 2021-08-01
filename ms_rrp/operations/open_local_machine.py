from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, AsyncIterator, cast
from struct import pack as struct_pack, unpack as struct_unpack
from contextlib import asynccontextmanager

from msdsalgs.win32_error import Win32ErrorCode
from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response

from ms_rrp.operations import Operation
from ms_rrp.structures.regsam import Regsam
from ms_rrp.operations.base_reg_close_key import base_reg_close_key, BaseRegCloseKeyRequest


@dataclass
class OpenLocalMachineResponse(ClientProtocolResponseBase):
    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> OpenLocalMachineResponse:
        return cls(
            key_handle=data[:20],
            return_code=Win32ErrorCode(struct_unpack('<I', data[20:24])[0])
        )

    def __bytes__(self) -> bytes:
        return self.key_handle + struct_pack('<I', self.return_code)


@dataclass
class OpenLocalMachineRequest(ClientProtocolRequestBase):
    OPERATION: ClassVar[Operation] = Operation.OPEN_LOCAL_MACHINE
    _RESERVED_SERVER_NAME: ClassVar[bytes] = bytes(4)

    sam_desired: Regsam

    @classmethod
    def from_bytes(cls, data: bytes) -> OpenLocalMachineRequest:
        # TODO: Check reserved `ServerName` if `strict_check` is set.
        return cls(sam_desired=Regsam.from_int(struct_unpack('<I', data[4:8])[0]))

    def __bytes__(self) -> bytes:
        return self._RESERVED_SERVER_NAME + struct_pack('<I', int(self.sam_desired))


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
