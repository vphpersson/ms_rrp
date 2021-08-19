from __future__ import annotations
from dataclasses import dataclass
from typing import ByteString
from struct import unpack_from

from ndr.structures import NDRType


@dataclass
class RpcHkey(NDRType):

    representation: bytes

    def __bytes__(self) -> bytes:
        return self.representation

    @classmethod
    def from_bytes(cls, data: ByteString, offset: int = 0) -> RpcHkey:
        return cls(representation=unpack_from('<20s', buffer=data, offset=offset)[0])
