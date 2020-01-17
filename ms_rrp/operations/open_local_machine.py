from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar
from struct import pack as struct_pack, unpack as struct_unpack

from rpc.connection import Connection as RPCConnection
from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase, obtain_response
from msdsalgs.win32_error import Win32ErrorCode

from ms_rrp.operations import Operation
from ms_rrp.structures.regsam import Regsam


@dataclass
class OpenLocalMachineResponse(ClientProtocolResponseBase):
    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> OpenLocalMachineResponse:
        return cls(key_handle=data[:20], return_code=Win32ErrorCode(struct_unpack('<I', data[20:24])[0]))

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


async def open_local_machine(
    rpc_connection: RPCConnection,
    request: OpenLocalMachineRequest,
    raise_exception: bool = True
) -> OpenLocalMachineResponse:
    """
    Perform the OpenLocalMachine operation.

    :param rpc_connection:
    :param request:
    :param raise_exception:
    :return:
    """

    return await obtain_response(rpc_connection=rpc_connection, request=request, raise_exception=raise_exception)