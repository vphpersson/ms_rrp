from __future__ import annotations
from dataclasses import dataclass
from struct import unpack as struct_unpack, pack as struct_pack

from ndr.structures.conformant_varying_string import ConformantVaryingString
from ndr.structures.pointer import Pointer, NullPointer


@dataclass
class RRPUnicodeString:
    representation: str

    @property
    def representation_bytes(self) -> bytes:
        return (self.representation + '\x00').encode(encoding='utf-16-le')

    @classmethod
    def from_bytes(cls, data: bytes) -> RRPUnicodeString:
        length: int = struct_unpack('<H', data[:2])[0]
        maximum_length: int = struct_unpack('<H', data[2:4])[0]

        ndr_string = ConformantVaryingString.from_bytes(
            data=data[4+Pointer.structure_size:4+Pointer.structure_size+ConformantVaryingString.STRUCTURE_SIZE+length]
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
            struct_pack('<H', string_len),
            struct_pack('<H', string_len),
            bytes(pointer)
        ])

    def __len__(self) -> int:
        return len(self.__bytes__())
