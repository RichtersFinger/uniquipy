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
                f"Error: Invalid argument for input directory {input_dir}, directory does not exist.",
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
    is_unique, uniques = src.find_duplicates(
        list_of_files,
        hash_algorithm,
        progress_hook=src.default_progress_hook if verbose else None
    )

    # print results
    if verbose:
        click.echo("")
        click.echo(f"number of unique files: {len(uniques)}")

        if is_unique:
            click.echo("no duplicates found")
        else:
            click.echo("there are duplicates")

        # list duplicates
        click.echo("="*5 + " Details " + "="*5)
        for files in uniques.values():
            if len(files) > 1:
                click.echo(f"file '{files[0]}' has duplicate(s) at")
                click.echo("\n".join(map(lambda x: f" * {str(x)}", files[1:])))

        click.echo("="*5 + " Summary " + "="*5)
        click.echo(f"total number of duplicate files: {len(list_of_files) - len(uniques)}")
    else:
        # arrange in blocks
        click.echo(
            "\n\n".join(
                "\n".join(map(str, files)) for files in uniques.values()
            )
        )
