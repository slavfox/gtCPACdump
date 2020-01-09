# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import struct

read_error = struct.error


def read_type(stream, t):
    # Wrapper around struct.unpack to make it less ugly to use
    res = struct.unpack(f"<{t}", stream.read(struct.calcsize(f"<{t}")))
    if len(res) == 1:
        return res[0]
    else:
        return res


# Colors
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
