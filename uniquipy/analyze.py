"""
This module contains the definition of the analyze-command.
"""

import sys
from pathlib import Path
import click
from uniquipy import src
from uniquipy.src import HASHING_ALGORITHMS as methods


@click.command()
@click.option(
    "-i", "--input-directory", "input_dir",
    required=True,
    type=click.Path(exists=True),
    help="path to the input directory"
)
@click.option(
    "-m", "--hash-algorithm", "hash_algorithm",
    default=list(methods.keys())[0],
    show_default=True,
    type=click.Choice(
        list(methods.keys()),
        case_sensitive=True
    ),
    help="specify the hash algorithm used to identify files"
)
@click.option(
    "-v", "--verbose", "verbose",
    is_flag=True,
    help="verbose output"
)
def analyze(
    input_dir,
    hash_algorithm,
    verbose
):
    """Analyze existing directory regarding file duplicates."""

    source = Path(input_dir)

    # make sure the target is valid
    if not source.is_dir():
        if verbose:
            click.echo(
                f"Invalid argument for input directory: {input_dir}",
                file=sys.stderr
            )
        sys.exit(1)

    if verbose:
        click.echo("analyzing..")

    # find all files
    list_of_files = [p for p in source.glob("**/*") if p.is_file()]

    if verbose:
        click.echo(f"working on a set of {len(list_of_files)} files")

    uniques = {}

    # first, discriminate by file-size
    uniques_st_size = {}
    is_unique = True
    for file in list_of_files:
        st_size = file.stat().st_size
        if st_size not in uniques_st_size:
            uniques_st_size[st_size] = []
        else:
            is_unique = False
        uniques_st_size[st_size].append(file)

    uniques_hashed_chunks = {}
    # second (if necessary), use first chunk of bytes
    if not is_unique:
        if verbose:
            click.echo(
                "file size suggests duplicate files, continue with hashing first chunks.."
            )
        is_unique = True
        for files in uniques_st_size.values():
            for file in files:
                hashed_chunk = src.hash_from_file(
                    hash_algorithm,
                    str(file),
                    short=True
                )
                if hashed_chunk not in uniques_hashed_chunks:
                    uniques_hashed_chunks[hashed_chunk] = []
                else:
                    is_unique = False
                uniques_hashed_chunks[hashed_chunk].append(file)
    else:
        uniques = uniques_st_size

    uniques_hashed = {}
    # third (if necessary), use entire file for hashing
    if not is_unique:
        if verbose:
            click.echo(
                "first chunk suggests duplicate files, continue with hashing entire files.."
            )
        is_unique = True
        for files in uniques_hashed_chunks.values():
            for file in files:
                hashed_chunk = src.hash_from_file(
                    hash_algorithm,
                    str(file)
                )
                if hashed_chunk not in uniques_hashed:
                    uniques_hashed[hashed_chunk] = []
                else:
                    is_unique = False
                uniques_hashed[hashed_chunk].append(file)

        uniques = uniques_hashed
    else:
        uniques = uniques_hashed_chunks

    click.echo(f"number of unique files: {len(uniques)}")
    click.echo(f"{uniques}")
