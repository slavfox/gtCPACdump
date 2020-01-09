# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import argparse
from pathlib import Path

from gtcpacdump.common import OKBLUE, OKGREEN, WARNING, FAIL, ENDC, BOLD
from gtcpacdump.cpac import CPAC
from gtcpacdump.subarchive import SubArchive


class GhostTrickDumper:
    def __init__(self, path_to_cpac: Path, output_dir: Path, mode: str):
        print(
            f"{OKBLUE}{BOLD}Initializing "
            f"{WARNING}Ghost Trick CPAC dumper{ENDC}{BOLD}{OKBLUE}.{ENDC}"
        )
        self.mode = mode
        self.path_to_cpac2d = path_to_cpac
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
        self.cpac = CPAC(self.path_to_cpac2d)
        self.cpac.parse_subfiles()

    def dump_backgrounds(self):
        print(f"{OKBLUE}Preparing to extract backgrounds in .{ENDC}")
        bgs_subarchive = self.load_subarchive(4)
        bgs_dir = self.output_dir / "4"
        print(f"{OKBLUE}{BOLD}Extracting backgrounds.{ENDC}")
        bgs_dir.mkdir(parents=True, exist_ok=True)
        for i in range(1, len(bgs_subarchive.subfiles)):
            print(f"{OKBLUE}Dumping background {WARNING}{i}{OKBLUE}...{ENDC}")
            try:
                im = bgs_subarchive.dump_image(i)
                im_path = bgs_dir / f"bg_{i}.png"
                with im_path.open("wb") as f:
                    im.save(f)
                    print(f"{OKGREEN}Saved as {ENDC}{im_path}{OKGREEN}!{ENDC}")
            except Exception:  # ToDo
                print(f"{FAIL}Fail.{ENDC}")

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract cpac_2d.bin files from Ghost Trick."
    )
    parser.add_argument(
        "input_path", help="Path to cpac_2d.bin", type=Path,
    )
    parser.add_argument(
        "--mode",
        choices=["nds", "ios"],
        default="nds",
        metavar="MODE",
        help="Extraction mode: either 'nds' (default) or 'ios'.",
    )
    parser.add_argument(
        "action",
        choices=["backgrounds"],
        nargs="?",
        default="backgrounds",
        help="What to extract. Right now, only 'backgrounds' (default) is "
        "accepted",
    )
    parser.add_argument(
        "output_dir", help="Path to the output directory", type=Path
    )
    args = parser.parse_args()

    dumper = GhostTrickDumper(args.input_path, args.output_dir, args.mode)
    if args.action == "backgrounds":
        dumper.dump_backgrounds()
