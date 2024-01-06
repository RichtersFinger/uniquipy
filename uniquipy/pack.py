"""
This module contains the definition of the pack- and unpack-commands.
"""

import sys
from shutil import copy
from pathlib import Path
from datetime import datetime
from importlib.metadata import version
import click
from uniquipy import src
from uniquipy.src import HASHING_ALGORITHMS as methods


data_dir_name = "data"
index_file_name = "index.txt"


@click.command()
@click.option(
    "-i", "--input-directory", "input_dir",
    required=True,
    type=click.Path(exists=True),
    help="path to the input directory"
)
@click.option(
    "-o", "--output-directory", "output_dir",
    required=True,
    type=click.Path(exists=False),
    help="path to the (empty) output directory"
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
def pack(
    input_dir,
    output_dir,
    hash_algorithm,
    verbose
):
    """
    Pack the files of an existing directory into a unique format regarding file
    duplicates.
    """

    source = Path(input_dir)
    destination = Path(output_dir)

    # make sure the target is valid
    if not source.is_dir():
        if verbose:
            click.echo(
                f"Error: Invalid argument for input directory {input_dir}, directory does not exist.",
                file=sys.stderr
            )
        sys.exit(1)
    # make sure the destination is valid
    if destination.exists():
        if verbose:
            click.echo(
                f"Error: Invalid argument for output directory {output_dir}, directory already exists.",
                file=sys.stderr
            )
        sys.exit(1)

    if verbose:
        click.echo("analyzing..")

    # find all files
    list_of_files = [p for p in source.glob("**/*") if p.is_file()]

    if verbose:
        click.echo(f"working on a set of {len(list_of_files)} files")

    # run analysis
    _, uniques = src.find_duplicates(
        list_of_files,
        hash_algorithm,
        progress_hook=src.default_progress_hook if verbose else None
    )

    if verbose:
        click.echo("\npacking..")

    # write readme
    destination.mkdir(parents=True, exist_ok=False)

    readme = destination / "readme.txt"
    readme.write_text(f"""This archive has been generated with uniquipy v{version('uniquipy')} using the '{hash_algorithm}'-hashing method at {datetime.now().isoformat()}
See https://github.com/RichtersFinger/uniquipy for details.

The data-directory contains a copy of the original directory where duplicates of files have been removed.
Its original state can be restored with the 'unpack' command of uniquipy.
""", encoding="utf-8")

    # write index
    index = destination / index_file_name
    index.write_text(
        "\n\n".join(
            "\n".join(
                map(lambda file: str(file.relative_to(source)), files)
            ) for files in uniques.values()
        ),
        encoding="utf-8"
    )

    # write data
    for progress, files in enumerate(uniques.values()):
        file = files[0]

        file_destination = destination / data_dir_name / file.relative_to(source)
        file_destination.parent.mkdir(parents=True, exist_ok=True)
        copy(file, file_destination)

        if verbose:
            src.default_progress_hook(
                stage="copying data",
                progress=(progress, len(uniques))
            )

    if verbose:
        click.echo(f"\ncopied {str(len(uniques))} files")
        click.echo(f"built archive of unique files at {str(destination)}")


@click.command()
@click.option(
    "-i", "--input-directory", "input_dir",
    required=True,
    type=click.Path(exists=True),
    help="path to the (previously packed) input directory"
)
@click.option(
    "-o", "--output-directory", "output_dir",
    required=True,
    type=click.Path(exists=False),
    help="path to the (empty) output directory"
)
@click.option(
    "-v", "--verbose", "verbose",
    is_flag=True,
    help="verbose output"
)
def unpack(
    input_dir,
    output_dir,
    verbose
):
    """
    Unpack, i.e., reconstruct a previously packed directory at a given
    destination.
    """

    source = Path(input_dir)
    destination = Path(output_dir)

    # make sure the target is valid
    if not source.is_dir() \
            or not (source / index_file_name).is_file() \
            or not (source / data_dir_name).is_dir():
        if verbose:
            click.echo(
                f"Error: Invalid argument for input directory {input_dir}, directory does not exist or has a bad format (expected 'index.txt' and 'data/').",
                file=sys.stderr
            )
        sys.exit(1)
    # make sure the destination is valid
    if destination.exists():
        if verbose:
            click.echo(
                f"Error: Invalid argument for output directory {output_dir}, directory already exists.",
                file=sys.stderr
            )
        sys.exit(1)

    if verbose:
        click.echo("reconstructing..")

    # read data
    index = (source / index_file_name).read_text(encoding="utf-8")
    uniques = index.split("\n\n")

    for progress, unique in enumerate(uniques):
        files = unique.split("\n")
        for file in files:
            (destination / file).parent.mkdir(parents=True, exist_ok=True)
            copy(source / "data" / files[0], destination / file)

        if verbose:
            src.default_progress_hook(
                stage="making duplicates",
                progress=(progress, len(uniques))
            )

    if verbose:
        click.echo("")
        click.echo(f"rebuild from archive of unique files at {str(destination)}")
