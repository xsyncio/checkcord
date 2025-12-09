import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from checkcord.cli.runner import run_checks
from checkcord.core.config import load_config, save_config
from checkcord.core.generator import (
    DictionaryGenerator,
    LeetGenerator,
    PatternGenerator,
    RandomCharGenerator,
    RemoteListGenerator,
)

console = Console()


class Wizard:
    def __init__(self):
        self.config = load_config()

    def show_header(self):
        console.clear()

        # Discord Palette
        # Blurple: #5865F2, Green: #57F287, Yellow: #FEE75C
        # Fuchsia: #EB459E, Red: #ED4245, White: #FFFFFF

        banner_text = r"""
 ▄▄▄▄▄▄▄ ▄▄                        ▄▄▄▄▄▄▄                ▄▄ 
███▀▀▀▀▀ ██                ▄▄     ███▀▀▀▀▀                ██ 
███      ████▄ ▄█▀█▄ ▄████ ██ ▄█▀ ███      ▄███▄ ████▄ ▄████ 
███      ██ ██ ██▄█▀ ██    ████   ███      ██ ██ ██ ▀▀ ██ ██ 
▀███████ ██ ██ ▀█▄▄▄ ▀████ ██ ▀█▄ ▀███████ ▀███▀ ██    ▀████ 
"""
        from rich.text import Text

        # Create a gradient-like effect using Discord colors
        colors = ["#5865F2", "#57F287", "#FEE75C", "#EB459E", "#ED4245"]

        text = Text()
        try:
            # Try reading local banner.txt if it exists for customizing
            with open("banner.txt") as f:
                banner_text = f.read()
        except FileNotFoundError:
            pass

        lines = banner_text.splitlines()
        for i, line in enumerate(lines):
            color = colors[i % len(colors)]
            text.append(line + "\n", style=color)

        console.print(
            Panel(
                text, style="#5865F2", subtitle="[white]v1.1 (Modular Refactor)[/white]"
            )
        )

    def main_menu(self):
        while True:
            self.show_header()
            console.print("[1] [bold green]Generate & Check Usernames[/bold green]")
            console.print("[2] [bold yellow]Check from File[/bold yellow]")
            console.print("[3] [bold blue]Settings / Config[/bold blue]")
            console.print("[4] [bold red]Exit[/bold red]")

            choice = Prompt.ask(
                "Select an option", choices=["1", "2", "3", "4"], default="1"
            )

            if choice == "1":
                asyncio.run(self.generator_wizard())
            elif choice == "2":
                self.check_file_wizard()
            elif choice == "3":
                self.settings_wizard()
            elif choice == "4":
                console.print("[bold red]Goodbye![/bold red]")
                break

            if choice != "4":
                Prompt.ask("\nPress [bold]Enter[/bold] to continue...")

    async def generator_wizard(self):
        console.print("\n[bold cyan]Select Generator Method:[/bold cyan]")
        console.print("[1] Random Characters (e.g. 'xc._')")
        console.print("[2] Remote Wordlist (Xsyncio Gist)")
        console.print("[3] Pattern (e.g. 'cool_{random}')")
        console.print("[4] Dictionary (Adjective + Noun)")
        console.print("[5] Leet Speak (e.g. 'v1p3r')")

        choice = Prompt.ask("Method", choices=["1", "2", "3", "4", "5"], default="1")
        generator = None

        if choice == "1":
            length = IntPrompt.ask("Length", default=4)
            generator = RandomCharGenerator(length=length)
        elif choice == "2":
            url = Prompt.ask("Gist URL (Leave empty for default)", default="")
            if not url:
                generator = RemoteListGenerator()
            else:
                generator = RemoteListGenerator(url=url)
        elif choice == "3":
            pattern = Prompt.ask(
                "Pattern (use {random} for variable part)", default="user_{random}"
            )
            generator = PatternGenerator(pattern=pattern)
        elif choice == "4":
            add_numbers = Confirm.ask("Add random numbers to end?", default=False)
            generator = DictionaryGenerator(add_numbers=add_numbers)
        elif choice == "5":
            base_word = Prompt.ask("Enter base word to leet-ify")
            generator = LeetGenerator(base_word=base_word)

        count = IntPrompt.ask("How many usernames to generate?", default=10)

        if generator:
            console.print(
                f"[green]Generating {count} usernames using {generator.name}...[/green]"
            )
            usernames = await generator.generate(count)

            if not usernames:
                console.print("[red]No usernames generated![/red]")
                return

            await run_checks(usernames, self.config)

    def check_file_wizard(self):
        path = Prompt.ask("Enter the path to the username file")
        try:
            with open(path) as f:
                usernames = [line.strip() for line in f if line.strip()]
            asyncio.run(run_checks(usernames, self.config))
        except FileNotFoundError:
            console.print("[red]File not found![/red]")
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")

    def settings_wizard(self):
        console.print("\n[bold blue]Current Settings:[/bold blue]")
        console.print(
            f"Token: {self.config.token[:10]}..."
            if len(self.config.token) > 10
            else f"Token: {self.config.token}"
        )
        console.print(f"Threads: {self.config.thread_count}")
        console.print(f"Retry Delay: {self.config.retry_delay}s")
        console.print(f"Webhook: {self.config.webhook_url or 'None'}")

        if Confirm.ask("Edit settings?"):
            new_token = Prompt.ask("Token", default=self.config.token)
            new_threads = IntPrompt.ask(
                "Threads (1-50)", default=self.config.thread_count
            )
            # new_delay = FloatPrompt.ask("Retry Delay", default=self.config.retry_delay)
            # Fixed FloatPrompt import above
            new_delay = FloatPrompt.ask("Retry Delay", default=self.config.retry_delay)

            self.config.token = new_token
            self.config.thread_count = new_threads
            self.config.retry_delay = new_delay

            webhook = Prompt.ask(
                "Webhook URL (Empty to remove)",
                default=str(self.config.webhook_url) if self.config.webhook_url else "",
            )
            if webhook:
                try:
                    from pydantic import HttpUrl

                    # Forces validation/coercion
                    self.config.webhook_url = HttpUrl(webhook)
                except Exception:
                    console.print("[red]Invalid URL format ignored.[/red]")
            else:
                self.config.webhook_url = None

            save_config(self.config)
            console.print("[green]Settings saved![/green]")


def run_wizard():
    wizard = Wizard()
    wizard.main_menu()
