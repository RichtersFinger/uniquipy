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

    is_unique, uniques = src.find_duplicates(
        list_of_files,
        hash_algorithm
    )

    if is_unique:
        click.echo("entire set of files appears to be unique")
    else:
        click.echo("set of files appears to have duplicates")

    click.echo(f"number of unique files: {len(uniques)}")
    click.echo(f"{uniques}")
