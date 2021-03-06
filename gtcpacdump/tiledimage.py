# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from PIL import Image
from io import BytesIO
from .common import read_type

from gtcpacdump.common import OKBLUE, OKGREEN, ENDC
from .tileutils import (
    read_rgb555_palette,
    read_tile,
    dump_tile,
)


class TiledImage:
    def __init__(self, data: bytes, tile_size=(8,8)):
        self._data = BytesIO(data)
        self.width = 0
        self.height = 0
        self.tile_size = tile_size
        self.tiles = []
        self.palette = None

    def parse(self):
        print(f"  {OKBLUE}Loading image.{ENDC}")
        self._data.seek(0)
        self.width, flags = read_type(self._data, "HH")
        self.height = flags & ~0x00008000
        nibbles = bool(flags & 0x00008000)
        if self.width % self.tile_size[0]:
            raise ValueError(
                f"The width {self.width} has to be evenly "
                f"divideable "
                "by the tile width!"
            )
        if self.height % self.tile_size[1]:
            raise ValueError(
                "The height has to be evenly divideable " "by the tile height!"
            )
        bpp = 4 if nibbles else 8
        self._data.seek(512)
        self.palette = read_rgb555_palette(self._data, bpp)

        tile_count = (self.width // self.tile_size[0]) * (self.height // self.tile_size[1])
        self.tiles = []
        for i in range(tile_count):
            self.tiles.append(read_tile(bpp, self._data, self.tile_size))
        print(
            f"  {OKGREEN}Loaded {ENDC}{tile_count}{OKGREEN}-tile, "
            f"{ENDC}{self.width}x{self.height}{OKGREEN}px image.{ENDC}"
        )

    def dump(self, transparent: bool) -> Image:
        print(f"  {OKBLUE}Dumping image.{ENDC}")
        image = Image.new("RGBA", (self.width, self.height),)
        xtiles = self.width // self.tile_size[0]
        ytiles = self.height // self.tile_size[1]

        bigtileheight = 2
        bigtilewidth = 2
        bigtilearea = bigtilewidth * bigtileheight
        bigxtiles = xtiles // bigtilewidth
        bigytiles = ytiles // bigtileheight

        for bigypos in range(bigytiles):
            for bigxpos in range(bigxtiles):
                for smallypos in range(bigtileheight):
                    totalypos = (bigypos * bigtileheight) + smallypos
                    dest_y = totalypos * self.tile_size[1]
                    for smallxpos in range(bigtilewidth):
                        totalxpos = (bigxpos * bigtilewidth) + smallxpos
                        dest_x = totalxpos * self.tile_size[0]

                        tile_index = (
                            bigtilearea * (bigxpos + (bigypos * bigxtiles))
                        ) + (smallxpos + (smallypos * bigtilewidth))
                        tile = dump_tile(
                            self.tiles[tile_index],
                            self.palette,
                            0,
                            transparent,
                            self.tile_size
                        )
                        image.paste(
                            tile, (dest_x, dest_y,),
                        )

        print(f"  {OKGREEN}Done.{ENDC}")
        return image
