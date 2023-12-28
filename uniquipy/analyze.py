"""
This module contains the definition of the analyze-command.
"""

import click

@click.command()
@click.option("-i", "--input-directory", "input_dir",
    required=True,
    type=click.Path(exists=True),
    help="path to the input directory"
)
@click.option("-v", "--verbose", "verbose",
    is_flag=True,
    help="verbose output"
)
def analyze(
    input_dir,
    verbose
):
    """Analyze existing directory regarding file duplicates."""

    click.echo("analyzing..")
