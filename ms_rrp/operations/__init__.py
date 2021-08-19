from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import ClassVar
from enum import IntEnum

from rpc.utils.client_protocol_message import ClientProtocolRequestBase, ClientProtocolResponseBase
from rpc.utils.types import DWORD
from msdsalgs.win32_error import Win32ErrorCode
from ndr.structures.pointer import NullPointer

from ms_rrp.structures.regsam import Regsam
from ms_rrp.structures.rpc_hkey import RpcHkey


@dataclass
class OpenRootKeyResponse(ClientProtocolResponseBase, ABC):
    key_handle: bytes

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        'key_handle': (RpcHkey,),
        'return_code': (DWORD, Win32ErrorCode)
    }


@dataclass
class OpenRootKeyRequest(ClientProtocolRequestBase, ABC):
    sam_desired: Regsam

    _STRUCTURE: ClassVar[dict[str, tuple[...]]] = {
        '__server_name': (NullPointer,),
        'sam_desired': (DWORD, Regsam.from_int)
    }

    @property
    def server_name(self) -> bytes:
        return bytes(4)


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

