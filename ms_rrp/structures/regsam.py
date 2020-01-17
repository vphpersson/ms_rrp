from enum import IntFlag
from msdsalgs.utils import Mask


class RegsamFlag(IntFlag):
    KEY_QUERY_VALUE = 0x00000001
    KEY_SET_VALUE = 0x00000002
    KEY_CREATE_SUB_KEY = 0x00000004
    KEY_ENUMERATE_SUB_KEYS = 0x00000008
    KEY_CREATE_LINK = 0x00000020
    KEY_WOW64_64KEY = 0x00000100
    KEY_WOW64_32KEY = 0x00000200


Regsam = Mask.make_class(
    int_flag_class=RegsamFlag,
    prefix='KEY_'
)
