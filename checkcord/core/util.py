import logging

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
    )


def get_console() -> Console:
    return Console()


logger = logging.getLogger("checkcord")
