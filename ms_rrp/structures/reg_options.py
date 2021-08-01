from enum import IntFlag
from msdsalgs.utils import Mask


class RegOptionsFlag(IntFlag):
    REG_OPTION_VOLATILE = 0x00000001
    REG_OPTION_BACKUP_RESTORE = 0x00000004
    REG_OPTION_OPEN_LINK = 0x00000008
    REG_OPTION_DONT_VIRTUALIZE = 0x00000010


RegOptions = Mask.make_class(
    int_flag_class=RegOptionsFlag,
    prefix='REG_OPTION_'
)
