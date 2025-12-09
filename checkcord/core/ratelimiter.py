import asyncio

from rich.console import Console

console = Console()


class GlobalRateLimiter:
    def __init__(self, initial_delay: float = 0.5):
        self.lock = asyncio.Lock()
        self.current_delay = initial_delay
        self.paused_until: float = 0
        self.is_paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Initially set, meaning "go"

    async def wait_for_token(self):
        """Wait for permission to make a request."""
        # Check if we are globally paused
        await self._pause_event.wait()

        # Apply the current delay
        await asyncio.sleep(self.current_delay)

    async def trigger_backoff(self, retry_after: float):
        """Trigger a global pause and increase delay."""
        async with self.lock:
            # If already paused, check if we need to extend it
            if not self._pause_event.is_set():
                if retry_after > self.current_delay:
                    # Log only if significantly longer
                    pass
                return

            console.print(
                f"[bold yellow]⚠️ Global Rate Limit Hit! Pausing all threads for {retry_after:.2f}s...[/bold yellow]"
            )
            self._pause_event.clear()
            self.current_delay = max(
                self.current_delay * 1.5, 1.0
            )  # Increase base delay

            # Spin up a task to clear the pause after duration
            asyncio.create_task(self._reset_pause(retry_after))

    async def _reset_pause(self, duration: float):
        await asyncio.sleep(duration)
        self._pause_event.set()
        console.print(
            f"[bold green]✅ Resuming requests (New delay: {self.current_delay:.2f}s)[/bold green]"
        )
