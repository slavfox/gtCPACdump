# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from dataclasses import dataclass
from io import BytesIO

from gtcpacdump.common import OKBLUE, OKGREEN, WARNING, ENDC
from .common import read_type
from .compression import stock_decompress
from .tiledimage import TiledImage


@dataclass
class SubfileEntry:
    offset: int
    size: int = None
    compressed: bool = False
    unknown_flag: bool = False


def read_section_table(stream: BytesIO,) -> dict:
    section_table = {}

    size, sections = read_type(stream, "II")

    for i in range(sections):
        section_name = stream.read(4)
        section_table[section_name] = read_type(stream, "I")

    return section_table


class SubArchive:
    def __init__(self, data: bytes):
        self._data = BytesIO(data)
        self.subfiles = []
        self.data_base_offset = 0

    def dump_image(self, idx):
        image = self.open(idx)
        if not image:
            return None
        image = TiledImage(image)
        image.parse()
        return image.dump(False)

    def readYEKB(self, start, data_base_offset):
        print(
            f"    {OKBLUE}Reading YEKB section{ENDC}...", end="",
        )
        self._data.seek(start)

        subfiles = []
        while True:
            mixed1, mixed2 = read_type(self._data, "II")
            compressed = bool(mixed2 & 0x80000000)
            unknown_flag = bool(mixed1 & 0x80000000)
            size = mixed2 & ~0x80000000
            offset = mixed1 & ~0x80000000
            if size != 0:
                subfiles.append(
                    SubfileEntry(
                        offset=offset,
                        size=size,
                        compressed=compressed,
                        unknown_flag=unknown_flag,
                    )
                )
            if self._data.tell() >= data_base_offset:
                break
        print(
            f"{OKGREEN}OK!\n    "
            f"Found {WARNING}{len(subfiles)}{OKGREEN} subfiles.{ENDC}"
        )
        self.subfiles = subfiles

    def readYEKP(self, start, data_base_offset):
        print(
            f"    {OKBLUE}Reading YEKP section{ENDC}...", end="",
        )
        self._data.seek(start)

        subfiles = []
        while True:
            mixed = read_type(self._data, "I")
            compressed = bool(mixed & 0x80000000)
            offset = mixed & ~0x80000000
            subfiles.append(
                SubfileEntry(offset=offset, compressed=compressed,)
            )
            if self._data.tell() >= data_base_offset:
                break

        stop = len(subfiles) - 3  # skip last
        for i, subfile in enumerate(subfiles[:stop]):
            subfile.size = subfiles[i + 1].offset - subfile.offset
            if subfile.size + subfile.offset >= len(self._data.getvalue()):
                raise ValueError("bork")

        print(
            f"{OKGREEN}OK!\n    "
            f"Found {WARNING}{len(subfiles)}{OKGREEN} subfiles.{ENDC}"
        )
        self.subfiles = subfiles

    def parse(self):
        print(f"  {OKBLUE}Parsing subarchive...{ENDC}")
        section_table = read_section_table(self._data)
        if b"TADB" in section_table:
            print(
                f"  {OKGREEN}Found {ENDC}TADB{OKGREEN} "
                f"data base section.{ENDC}"
            )
            self.data_base_offset = section_table[b"TADB"]
        elif b"TADP" in section_table:
            print(
                f"  {OKGREEN}Found {ENDC}TADP{OKGREEN} "
                f"data base section.{ENDC}"
            )
            self.data_base_offset = section_table[b"TADP"]
        else:
            raise ValueError("File has no data base section")

        if b"YEKB" in section_table:
            print(
                f"  {OKGREEN}Found {ENDC}YEKB{OKGREEN} "
                f"table base section.{ENDC}"
            )
            self.readYEKB(
                section_table[b"YEKB"], self.data_base_offset,
            )
        elif b"YEKP" in section_table:
            print(
                f"  {OKGREEN}Found {ENDC}YEKP{OKGREEN} "
                f"table base section.{ENDC}"
            )
            self.readYEKP(
                section_table[b"YEKP"], self.data_base_offset,
            )
        else:
            raise ValueError("File has no table base section")

    def open(self, id_: int) -> bytes:
        print(f"  {OKBLUE}Reading file {ENDC}{id_}{OKBLUE}.{ENDC}")
        self._data.seek(self.subfiles[id_].offset + self.data_base_offset)
        out = self._data.read(self.subfiles[id_].size)
        if self.subfiles[id_].compressed:
            print(f"    {OKBLUE}Decompressing file {ENDC}{id_}{OKBLUE}.{ENDC}")
            out = stock_decompress(out)
        return out
