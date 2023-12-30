![Tests](https://github.com/RichtersFinger/uniquipy/actions/workflows/tests.yml/badge.svg?branch=main)

# uniquipy
Minimal python cli-tool to find and handle file duplicates in a directory based on file hashes.

## Installation
Simply clone this repository and install using pip, i.e., in the repository's root directory, run
```
pip install .
```
It is recommended to install this package only to a virtual environment. (Create with `python3 -m venv venv` and activate an existing environment via `source venv/bin/activate`.)

## Usage
Run `uniquipy -h` to get usage information in the terminal. Use the verbose-option (`-v`) in below commands to get progress indicators and verbose feedback on results. In the following, optional arguments are given in the form of `[...]`.

In order to analyze a directory, run
```
uniquipy analyze -i <dir> [-m md5|sha1|sha256|sha512] [-v]
```

A directory can be transformed into a format where only single copies/unique files are stored explicitly (along with information on how to reconstruct the original source). To perform this transformation, use
```
uniquipy pack -i <dir> -o <dir> [-m md5|sha1|sha256|sha512] [-v]
```

In order to revert the `pack`-command, run
```
uniquipy unpack -i <dir> -o <dir> [-v]
```
The input directory (`-i`) expects a directory containing an `index.txt`-file and a `data/`-directory (as generated previously using `uniquipy pack ..`).
