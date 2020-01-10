# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pathlib import Path
from collections import namedtuple

from gtcpacdump.common import OKBLUE, OKGREEN, WARNING, ENDC
from .common import read_type

SubarchivePointer = namedtuple("Subfile", ("offset", "size"))


class CPAC:
    def __init__(self, cpac_2d_path: Path):
        self.cpac_path = cpac_2d_path
        self.subarchives = []

    def parse_subfiles(self):
        with self.cpac_path.open("rb") as f:
            print(
                f"  {OKBLUE}Reading {ENDC}{self.cpac_path.absolute()}"
                f"{OKBLUE}...{ENDC} ",
                end="",
            )
            self.subarchives = []
            while True:
                offset_size = read_type(f, "II")
                self.subarchives.append(SubarchivePointer(*offset_size))
                if f.tell() >= self.subarchives[0].offset:
                    break
            print(
                f"{OKGREEN}OK!\n  Found "
                f"{WARNING}{len(self.subarchives)}{OKGREEN} subfiles.{ENDC}"
            )

    def open(self, id_: int) -> bytes:
        with self.cpac_path.open("rb") as f:
            f.seek(self.subarchives[id_].offset)
            subfile = f.read(self.subarchives[id_].size)
        return subfile
