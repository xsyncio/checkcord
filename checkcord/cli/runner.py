import asyncio

from curl_cffi.requests import AsyncSession
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from checkcord.core.checker import DiscordChecker
from checkcord.core.util import get_console
from checkcord.models import AppConfig, CheckStatus

console = get_console()


async def run_checks(usernames: list[str], config: AppConfig):
    checker = DiscordChecker(config)

    console.print(
        f"[bold cyan]Starting check for {len(usernames)} usernames...[/bold cyan]"
    )

    # Mapping results for summary
    results_summary = {s: 0 for s in CheckStatus}
    valid_names: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task("Checking...", total=len(usernames))

        async with AsyncSession(impersonate="chrome") as session:
            # Create coroutines
            coroutines = [checker.check_username(session, u) for u in usernames]

            # Use asyncio.as_completed to update progress bar as they finish
            for coro in asyncio.as_completed(coroutines):
                result = await coro
                progress.advance(task_id)
                results_summary[result.status] += 1

                if result.status == CheckStatus.AVAILABLE:
                    console.print(f"[green]AVAILABLE: {result.username}[/green]")
                    valid_names.append(result.username)
                elif result.status == CheckStatus.RATE_LIMITED:
                    console.print(f"[yellow]RATE LIMITED: {result.username}[/yellow]")
                elif result.status == CheckStatus.ERROR:
                    console.print(
                        f"[red]ERROR: {result.username} - {result.message}[/red]"
                    )

    # Summary Table
    table = Table(title="Check Summary")
    table.add_column("Status", style="magenta")
    table.add_column("Count", style="cyan")

    for status, count in results_summary.items():
        color = (
            "green"
            if status == CheckStatus.AVAILABLE
            else "red"
            if status == CheckStatus.TAKEN
            else "yellow"
        )
        table.add_row(f"[{color}]{status.value}[/{color}]", str(count))

    console.print(table)

    if valid_names:
        with open("valid_usernames.txt", "a") as f:
            for name in valid_names:
                _ = f.write(f"{name}\n")
        count = len(valid_names)
        console.print(
            f"[bold green]Saved {count} valid usernames to valid_usernames.txt[/green]"
        )
