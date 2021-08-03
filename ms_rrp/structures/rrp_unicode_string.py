from __future__ import annotations
from dataclasses import dataclass
from typing import ByteString
from struct import unpack_from, pack

from ndr.structures.conformant_varying_string import ConformantVaryingString
from ndr.structures.pointer import Pointer, NullPointer


@dataclass
class RRPUnicodeString:
    representation: str

    @property
    def representation_bytes(self) -> bytes:
        return (self.representation + '\x00').encode(encoding='utf-16-le')

    @classmethod
    def from_bytes(cls, data: ByteString, base_offset: int = 0) -> RRPUnicodeString:
        data = memoryview(data)[base_offset:]
        offset = 0

        length: int = unpack_from('<H', buffer=data, offset=offset)[0]
        offset += 2

        maximum_length: int = unpack_from('<H', buffer=data, offset=offset)[0]
        offset += 2

        ndr_string = ConformantVaryingString.from_bytes(
            data=data[
                 offset+Pointer.structure_size
                 :
                 offset+Pointer.structure_size+ConformantVaryingString.STRUCTURE_SIZE+length
             ]
        )

        return cls(representation=ndr_string.representation)

    def __bytes__(self) -> bytes:
        if len(self.representation) == 0:
            pointer = NullPointer()
            string_len = 0
        else:
            pointer = Pointer(
                representation=ConformantVaryingString(representation=self.representation)
            )
            string_len = len(self.representation_bytes)

        return b''.join([
            pack('<H', string_len),
            pack('<H', string_len),
            bytes(pointer)
        ])

    def __len__(self) -> int:
        return len(self.__bytes__())
