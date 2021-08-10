from enum import Enum
from typing import Callable, Type

from ms_rrp.operations import OpenRootKeyRequest
from ms_rrp.operations.open_classes_root import open_classes_root, OpenClassesRootRequest
from ms_rrp.operations.open_current_user import open_current_user, OpenCurrentUserRequest
from ms_rrp.operations.open_local_machine import open_local_machine, OpenLocalMachineRequest
from ms_rrp.operations.open_performance_data import open_performance_data, OpenPerformanceDataRequest
from ms_rrp.operations.open_users import open_users, OpenUsersRequest


class OpenableRootKey(Enum):
    HKEY_CLASSES_ROOT = 'HKCR'
    HKEY_CURRENT_USER = 'HKCU'
    HKEY_LOCAL_MACHINE = 'HKLM'
    HKEY_PERFORMANCE_DATA = 'HKEY_PERFORMANCE_DATA'
    HKEY_USERS = 'HKU'


OPENABLE_ROOT_KEY_TO_OPERATION_AND_REQUEST: dict[OpenableRootKey, tuple[Callable, Type[OpenRootKeyRequest]]] = {
    OpenableRootKey.HKEY_CLASSES_ROOT: (open_classes_root, OpenClassesRootRequest),
    OpenableRootKey.HKEY_CURRENT_USER: (open_current_user, OpenCurrentUserRequest),
    OpenableRootKey.HKEY_LOCAL_MACHINE: (open_local_machine, OpenLocalMachineRequest),
    OpenableRootKey.HKEY_PERFORMANCE_DATA: (open_performance_data, OpenPerformanceDataRequest),
    OpenableRootKey.HKEY_USERS: (open_users, OpenUsersRequest)
}
