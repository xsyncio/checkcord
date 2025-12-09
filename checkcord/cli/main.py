import asyncio
from pathlib import Path
from typing import Annotated

import typer

from checkcord.cli.runner import run_checks
from checkcord.core.config import load_config
from checkcord.core.util import get_console, setup_logging

app = typer.Typer(
    name="CheckCord",
    help="A modern, high-performance Discord username checker and generator.",
    add_completion=False,
)
console = get_console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    CheckCord CLI.
    Run without commands to launch the Interactive Wizard.
    """
    if ctx.invoked_subcommand is None:
        from checkcord.cli.wizard import run_wizard

        run_wizard()


@app.command()
def wizard():
    """Launch the interactive wizard mode."""
    from checkcord.cli.wizard import run_wizard

    run_wizard()


@app.command()
def generate(
    count: int = typer.Option(1, help="Number of usernames to generate"),
    length: int = typer.Option(4, help="Length of the usernames generated"),
    dictionary: bool = typer.Option(
        False,
        help="Use a dictionary for words (Not implemented yet, uses random chars)",
    ),
):
    """Generate random usernames and check their availability."""
    from checkcord.core.generator import RandomCharGenerator

    config = load_config()
    setup_logging()

    if config.token == "YOUR_TOKEN_HERE" or config.token == "INVALID_TOKEN_LOAD_FAILED":
        console.print(
            "[bold red]Please configure your token in config.json![/bold red]"
        )
        return

    # Use the new generator module
    gen = RandomCharGenerator(length=length)
    usernames = asyncio.run(gen.generate(count))

    asyncio.run(run_checks(usernames, config))


FILE_PATH = typer.Argument(..., exists=True, help="Path to text file")


@app.command()
def check_list(
    file_path: Annotated[Path, FILE_PATH],
):
    """Check a list of usernames from a file."""
    config = load_config()
    setup_logging()

    if config.token == "YOUR_TOKEN_HERE":
        console.print(
            "[bold red]Please configure your token in config.json![/bold red]"
        )
        return

    with open(file_path) as f:
        usernames = [line.strip() for line in f if line.strip()]

    asyncio.run(run_checks(usernames, config))


def run():
    app()


if __name__ == "__main__":
    app()
