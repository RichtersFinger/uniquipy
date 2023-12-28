"""
This module defines the cli's entry-point.
"""

import click
from uniquipy.analyze import analyze
from uniquipy.pack import pack, unpack

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """
    Command line tool for finding and handling file duplicates in a directory
    based on file hashes.
    """

cli.add_command(analyze)
cli.add_command(pack)
cli.add_command(unpack)
