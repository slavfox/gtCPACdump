# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import argparse
from pathlib import Path

from gtcpacdump.common import OKBLUE, OKGREEN, WARNING, FAIL, ENDC, BOLD
from gtcpacdump.cpac import CPAC
from gtcpacdump.subarchive import SubArchive

BGS_SUBARCHIVE_IDX = 4


class GhostTrickDumper:
    def __init__(self, path_to_cpac: Path):
        print(
            f"{OKBLUE}{BOLD}Initializing "
            f"{WARNING}Ghost Trick CPAC dumper{ENDC}{BOLD}{OKBLUE}.{ENDC}"
        )
        self.path_to_cpac2d = path_to_cpac
        self.cpac = CPAC(self.path_to_cpac2d)
        self.cpac.parse_subfiles()

    def load_subarchive(self, i: int) -> SubArchive:
        print(
            f"{BOLD}{OKBLUE}Loading subarchive {WARNING}{i}{OKBLUE}{BOLD}."
            f" {ENDC}"
        )
        try:
            subarchive = SubArchive(self.cpac.open(i))
            subarchive.parse()
            print(f"{OKBLUE}Subarchive {WARNING}{i}{OKBLUE} loaded.{ENDC}")
            return subarchive
        except ValueError as e:
            print(f"{BOLD}{FAIL}ERROR: {WARNING}{e}.")


def init_dumper(args):
    return GhostTrickDumper(args.input_file)


def cmd_list_subarchives(args):
    dumper = init_dumper(args)
    for (offset, size) in dumper.cpac.subarchives:
        print(f"Offset: {offset}, size: {size}")


def cmd_list_subfiles(args):
    dumper = init_dumper(args)
    subarchive = dumper.load_subarchive(args.subarchive_index)
    for sfe in subarchive.subfiles:
        print(f"Offset: {sfe.offset}, size: {sfe.size}, compressed:"
              f" {sfe.compressed}, ?: {sfe.unknown_flag}")


def cmd_subarchive_images(args):
    dumper = init_dumper(args)
    subarchive = dumper.load_subarchive(args.subarchive_index)
    output_dir = args.output_dir / str(args.subarchive_index)
    output_dir.mkdir(parents=True, exist_ok=True)
    for i in range(1, len(subarchive.subfiles)):
        im = subarchive.dump_image(i, args.mode)
        im_path = output_dir / f"{i}.png"
        with im_path.open("wb") as f:
            im.save(f)


def cmd_dump_subfiles(args):
    dumper = init_dumper(args)
    subarchive = dumper.load_subarchive(args.subarchive_index)
    output_dir = args.output_dir / str(args.subarchive_index)
    output_dir.mkdir(parents=True, exist_ok=True)
    for i in range(1, len(subarchive.subfiles)):
        try:
            sf = subarchive.open(i, skip_decompression=True)
        except:
            continue
        sf_path = output_dir / f"{i}.bin"
        with sf_path.open("wb") as f:
            f.write(sf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract cpac_2d.bin files from Ghost Trick."
    )
    subparsers = parser.add_subparsers()
    subparsers.add_parser("list_subarchives", help="List "
                                                   "subarchives in the CPAC "
                                                   "file"
                                                   "").set_defaults(
        func=cmd_list_subarchives)

    subarchive_files = subparsers.add_parser("list_subfiles", help="List "
                                                                   "subfiles in the given subarchive")
    subarchive_files.set_defaults(func=cmd_list_subfiles)
    subarchive_files.add_argument('subarchive_index', type=int)

    dump_subfiles = subparsers.add_parser("dump_subfiles",
                                              help="Dump subfiles from a "
                                                   "given subarchive")
    dump_subfiles.set_defaults(func=cmd_dump_subfiles)
    dump_subfiles.add_argument('subarchive_index', type=int)
    dump_subfiles.add_argument(
        "output_dir", help="Path to the output directory", type=Path
    )

    subarchive_images = subparsers.add_parser("subarchive_images",
                                              help="Dump images from a given subarchive")
    subarchive_images.set_defaults(func=cmd_subarchive_images)
    subarchive_images.add_argument('subarchive_index', type=int)
    subarchive_images.add_argument(
        "--mode",
        choices=["nds", "ios"],
        default="nds",
        metavar="MODE",
        help="Extraction mode: either 'nds' (default) or 'ios'.",
    )
    subarchive_images.add_argument(
        "output_dir", help="Path to the output directory", type=Path
    )

    parser.add_argument(
        "-i", "--input-file", help="Path to cpac_2d.bin", type=Path,
        required=True
    )
    args = parser.parse_args()
    args.func(args)
