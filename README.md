# gtCPACdump
Ghost Trick cpac_2d.bin extractor.

```
Usage: ghosttrick.py [-h] [--mode MODE] input_path [{backgrounds}] output_dir

Extract cpac_2d.bin files from Ghost Trick.

positional arguments:
  input_path     Path to cpac_2d.bin
  {backgrounds}  What to extract. Right now, only 'backgrounds' (default) is accepted
  output_dir     Path to the output directory

optional arguments:
  -h, --help     show this help message and exit
  --mode MODE    Extraction mode: either 'nds' (default) or 'ios'.
```

Based heavily on [Henrik "Henke37" Andersson's original work on Nitro In a
 Flash][1].

Licensed [MPL-2.0](https://www.mozilla.org/en-US/MPL/2.0/) with his approval.

[1]: https://app.assembla.com/spaces/sdat4as/subversion/source/336
