from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, ByteString
from enum import IntEnum
from struct import Struct

from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase
from msdsalgs.win32_error import Win32ErrorCode

from ms_rrp.structures.regsam import Regsam


@dataclass
class OpenRootKeyResponse(ClientProtocolResponseBase, ABC):
    _KEY_HANDLE_STRUCT: ClassVar[Struct] = Struct('20s')

    key_handle: bytes

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> OpenRootKeyResponse:
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
class OpenRootKeyRequest(ClientProtocolRequestBase, ABC):
    _RESERVED_SERVER_NAME: ClassVar[bytes] = bytes(4)

    _SAM_DESIRED_STRUCT: ClassVar[Struct] = Struct('<I')

    sam_desired: Regsam

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> OpenRootKeyRequest:
        data = memoryview(data)[base_offset:]
        offset = 0

        # TODO: Check reserved `ServerName` if `strict` is set?
        offset += 4

        return cls(sam_desired=Regsam.from_int(cls._SAM_DESIRED_STRUCT.unpack_from(buffer=data, offset=offset)[0]))

    def __bytes__(self) -> bytes:
        return self._RESERVED_SERVER_NAME + self._SAM_DESIRED_STRUCT.pack(int(self.sam_desired))

    def __len__(self) -> int:
        return len(self._RESERVED_SERVER_NAME) + self._SAM_DESIRED_STRUCT.size


class Operation(IntEnum):
    OPEN_CLASSES_ROOT = 0
    OPEN_CURRENT_USER = 1
    OPEN_LOCAL_MACHINE = 2
    OPEN_PERFORMANCE_DATA = 3
    OPEN_USERS = 4
    BASE_REG_CLOSE_KEY = 5
    BASE_REG_CREATE_KEY = 6
    BASE_REG_DELETE_KEY = 7
    BASE_REG_DELETE_VALUE = 8
    BASE_REG_ENUM_KEY = 9
    BASE_REG_ENUM_VALUE = 10
    BASE_REG_FLUSH_KEY = 11
    BASE_REG_GET_KEY_SECURITY = 12
    BASE_REG_LOAD_KEY = 13
    OPNUM14_NOT_IMPLEMENTED = 14
    BASE_REG_OPEN_KEY = 15
    BASE_REG_QUERY_INFO_KEY = 16
    BASE_REG_QUERY_VALUE = 17
    BASE_REG_REPLACE_KEY = 18
    BASE_REG_RESTORE_KEY = 19
    BASE_REG_SAVE_KEY = 20
    BASE_REG_SET_KEY_SECURITY = 21
    BASE_REG_SET_VALUE = 22
    BASE_REG_UN_LOAD_KEY = 23
    OPNUM24_NOT_IMPLEMENTED = 24
    OPNUM25_NOT_IMPLEMENTED = 25
    BASE_REG_GET_VERSION = 26
    OPEN_CURRENT_CONFIG = 27
    OPNUM28_NOT_IMPLEMENTED = 28
    BASE_REG_QUERY_MULTIPLE_VALUES = 29
    OPNUM30_NOT_IMPLEMENTED = 30
    BASE_REG_SAVE_KEY_EX = 31
    OPEN_PERFORMANCE_TEXT = 32
    OPEN_PERFORMANCE_NLS_TEXT = 33
    BASE_REG_QUERY_MULTIPLE_VALUES2 = 34
    BASE_REG_DELETE_KEY_EX = 35

