# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""

"""
from PIL import Image
import numpy as np
from io import BytesIO
from .common import read_type


def scale_up(color):
    return color << 3 | color >> 2


def from555(color):
    r = scale_up(color & 0x1F)
    g = scale_up((color >> 5) & 0x1F)
    b = scale_up((color >> 10) & 0x1F)
    return b | (g << 8) | (r << 16)


def to_rgba(color):
    r = color >> 16 & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    r >>= 3
    g >>= 3
    b >>= 3
    return r * 8, g * 8, b * 8, 255


def read_rgb555_color(data: BytesIO):
    color = read_type(data, "H")
    return from555(color)


def read_rgb555_palette(data: BytesIO, bpp: int):
    palette_size = 16 if bpp == 4 else 256
    return [read_rgb555_color(data) for _ in range(palette_size)]


def read_tile(bpp: int, data: BytesIO, tile_size=(8, 8)):
    pixels = [0 for _ in range(tile_size[0] * tile_size[1])]
    if bpp == 4:
        for y in range(tile_size[1]):
            x = 0
            while x < tile_size[0]:
                nibble = read_type(data, "B")
                index = x + y * tile_size[0]
                pixels[index] = nibble & 0xF
                x += 1

                index = x + y * tile_size[0]
                pixels[index] = (nibble >> 4) & 0xF
                x += 1
    else:
        for y in range(tile_size[1]):
            x = 0
            while x < tile_size[0]:
                nibble = read_type(data, "B")
                index = x + y * tile_size[0]
                pixels[index] = nibble
                x += 1
    return pixels


def dump_tile(
    pixels, palette, palette_offset=0, use_transparency=True, tile_size=(8, 8)
):
    index = 0
    im_pixels = np.zeros((tile_size[1], tile_size[0], 4), dtype="uint8",)
    for y in range(tile_size[1]):
        for x in range(tile_size[0]):
            color = pixels[index]
            index += 1
            if color == 0 and use_transparency:
                im_pixels[x, y] = (
                    0,
                    255,
                    255,
                    0,
                )
            else:
                color = palette[color + palette_offset * 16]
                im_pixels[y, x] = to_rgba(color)
    image = Image.fromarray(im_pixels, "RGBA")
    return image
