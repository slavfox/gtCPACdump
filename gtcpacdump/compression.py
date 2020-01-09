# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from io import BytesIO
from typing import Tuple
from .common import read_type


def read_3_byte_uint(stream: BytesIO) -> int:
    i0, i1, i2 = read_type(stream, "BBB")
    return i0 | (i1 << 8) | (i2 << 16)


def stock_decompress(data: bytes) -> bytes:
    stream = BytesIO(data)
    typ = read_type(stream, "B")
    variant = typ & 0x0F
    typ >>= 4
    length = read_3_byte_uint(stream)
    compression = typ & ~8
    if compression == 0:
        data = stream.read(length)
    elif compression == 1:
        data = lz77_decode(stream, length, variant == 1)
    elif compression == 2:
        raise NotImplementedError("Huffman decompression not supported yet")
    elif compression == 3:
        raise NotImplementedError("RLE decompression not supported yet")
    else:
        raise ValueError("Unknown compression")

    if (typ & 8) == 8:
        raise ValueError("diffUnFilter not implemented yet")
    return data


def lz77_decode(
    stream: BytesIO, decoded_length: int, longlengths: bool
) -> bytes:
    bit = 0x0
    decoded = BytesIO()
    while len(decoded.getvalue()) < decoded_length:
        flagbyte = b"\0"
        bit = bit >> 1
        if bit > 4294967295:
            bit = 0
        if bit == 0:
            flagbyte = read_type(stream, "B")
            bit = 0x80

        if flagbyte & bit:
            if longlengths:
                (distance, length, readbyte,) = _lz77_longlengths_read_byte(
                    stream
                )
            else:
                readbyte = read_type(stream, "B")
                length = readbyte >> 4
                distance = readbyte & 0x0F << 8
                b = read_type(stream, "B")
                distance |= b
                length += 3

            if distance > len(decoded.getvalue()):
                raise ValueError("Hit seek past start of data")

            offset = len(decoded.getvalue()) - distance - 1
            readpos = offset
            for i in range(length):
                decoded.seek(readpos)
                readbyte = read_type(stream, "B")
                decoded.seek(0, 2)
                decoded.write(readbyte)
        else:
            b = read_type(stream, "B")
            decoded.write(b)
    return decoded.getvalue()


def _lz77_longlengths_read_byte(stream: BytesIO) -> Tuple[int, int, int]:
    readbyte = read_type(stream, "B")

    b = readbyte >> 4
    if b == 0:
        length = readbyte << 4
        readbyte = read_type(stream, "B")
        length |= readbyte >> 4
        length += 0x11

        distance = (readbyte & 0x0F) << 8
        readbyte = read_type(stream, "B")
        distance |= readbyte
    elif b == 1:
        length = (readbyte & 0xF) << 4
        readbyte = read_type(stream, "B")
        length |= readbyte << 4
        readbyte = read_type(stream, "B")
        length |= readbyte >> 4
        length += 0x111

        distance = (readbyte & 0x0F) << 8
        readbyte = read_type(stream, "B")
        distance |= readbyte
    else:
        length = (readbyte >> 4) + 1
        distance = (readbyte & 0x0F) << 8
        readbyte = read_type(stream, "B")
        distance |= readbyte
    return distance, length, readbyte
