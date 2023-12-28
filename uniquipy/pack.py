"""
This module contains the definition of the pack- and unpack-commands.
"""

import click
from uniquipy.src import HASHING_ALGORITHMS as methods

@click.command()
@click.option("-i", "--input-directory", "input_dir",
    required=True,
    type=click.Path(exists=True),
    help="path to the input directory"
)
@click.option("-o", "--output-directory", "output_dir",
    required=True,
    type=click.Path(exists=True),
    help="path to the (empty) output directory"
)
@click.option("-m", "--hash-algorithm", "hash_algorithm",
    default=list(methods.keys())[0],
    show_default=True,
    type=click.Choice(
        list(methods.keys()),
        case_sensitive=True
    ),
    help="specify the hash algorithm used to identify files"
)
@click.option("-v", "--verbose", "verbose",
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

    click.echo("packing..")

@click.command()
@click.option("-i", "--input-directory", "input_dir",
    required=True,
    type=click.Path(exists=True),
    help="path to the (previously packed) input directory"
)
@click.option("-o", "--output-directory", "output_dir",
    required=True,
    type=click.Path(exists=True),
    help="path to the (empty) output directory"
)
@click.option("-v", "--verbose", "verbose",
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

    click.echo("reconstructing..")
