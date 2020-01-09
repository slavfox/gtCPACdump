# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from collections import namedtuple
from io import BytesIO
from .common import read_type, read_error
from .compression import stock_decompress

Subfile = namedtuple("Subfile", ("offset", "size"))


class SplitArchive:
    def __init__(self, data: bytes):
        self._data = BytesIO(data)
        self.entries = []

    def parse(self):
        self.entries = []
        while True:
            try:
                (offset, length,) = read_type(self._data, "II")
                self.entries.append(Subfile(offset, length))
            except read_error:
                break

    def open(self, id_: int) -> bytes:
        self._data.seek(self.entries[id_].offset)
        return stock_decompress(self._data.read(self.entries[id_].size))
