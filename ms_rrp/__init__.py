from uuid import UUID
from typing import Final

from rpc.structures.presentation_syntax import PresentationSyntax

MS_RRP_ABSTRACT_SYNTAX: Final[PresentationSyntax] = PresentationSyntax(
    if_uuid=UUID('338cd001-2244-31f1-aaaa-900038001003'),
    if_version=1
)

MS_RRP_PIPE_NAME: Final[str] = 'winreg'
