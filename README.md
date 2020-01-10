# gtCPACdump
Ghost Trick cpac_2d.bin extractor.

```
usage: ghosttrick.py [-h] -i INPUT_FILE {list_subarchives,list_subfiles,dump_subfiles,subarchive_images} ...

Extract cpac_2d.bin files from Ghost Trick.

positional arguments:
  {list_subarchives,list_subfiles,dump_subfiles,subarchive_images}
    list_subarchives    List subarchives in the CPAC file
    list_subfiles       List subfiles in the given subarchive
    dump_subfiles       Dump subfiles from a given subarchive
    subarchive_images   Dump images from a given subarchive

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        Path to cpac_2d.bin
```

Based heavily on [Henrik "Henke37" Andersson's original work on Nitro In a
 Flash][1].

Licensed [MPL-2.0](https://www.mozilla.org/en-US/MPL/2.0/) with his approval.

[1]: https://app.assembla.com/spaces/sdat4as/subversion/source/336
