from enum import IntFlag
from msdsalgs.utils import Mask


class BaseRegOpenKeyOptionsFlag(IntFlag):
    REG_OPTION_BACKUP_RESTORE = 0x00000004
    REG_OPTION_OPEN_LINK = 0x00000008


BaseRegOpenKeyOptions = Mask.make_class(
    int_flag_class=BaseRegOpenKeyOptionsFlag,
    prefix='REG_OPTION_'
)
