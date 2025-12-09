import asyncio
import itertools
from collections.abc import Iterator
from typing import cast

from curl_cffi.requests import AsyncSession, Response

from checkcord.core.ratelimiter import GlobalRateLimiter
from checkcord.core.util import logger
from checkcord.models import (
    AppConfig,
    CheckResult,
    CheckStatus,
    WebhookEmbed,
    WebhookPayload,
)

# URL for non-destructive username availability check
URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"


class DiscordChecker:
    def __init__(self, config: AppConfig):
        self.config: AppConfig = config
        self.valid_usernames: list[str] = []
        self.headers: dict[str, str] = {
            "Authorization": config.token,
            "Content-Type": "application/json",
        }
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(config.thread_count)
        self.rate_limiter: GlobalRateLimiter = GlobalRateLimiter(
            initial_delay=config.retry_delay
        )

        self.proxies: list[str] = []
        self.proxy_cycle: Iterator[str] | None = None
        self._load_proxies()

    def _load_proxies(self):
        try:
            with open("proxies.txt") as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            if self.proxies:
                self.proxy_cycle = itertools.cycle(self.proxies)
                logger.info(f"Loaded {len(self.proxies)} proxies.")
        except FileNotFoundError:
            logger.info("No proxies.txt found, running directly.")

    async def check_username(self, session: AsyncSession, username: str) -> CheckResult:
        async with self.semaphore:
            # Global Rate Limit Wait
            await self.rate_limiter.wait_for_token()

            payload = {"username": username}
            proxy = next(self.proxy_cycle) if self.proxy_cycle else None

            try:
                # Use proxy if available
                # curl_cffi.requests.Response is not generic, so we don't need annotation on LHS if inferred correctly
                # But to satisfy "partially unknown" complaints or "not awaitable" we stick to explicit type
                response: Response = await session.post(  # type: ignore
                    URL, headers=self.headers, json=payload, proxy=proxy
                )

                # Handle Rate Limits Globally
                if response.status_code == 429:
                    try:
                        # json() returns Any, use cast. Suppress unknown member type from lib.
                        limit_data = cast(dict[str, object], response.json())  # type: ignore
                        # safe cast
                        ra_val = limit_data.get("retry_after", 5.0)
                        retry_after: float = (
                            float(ra_val)
                            if isinstance(ra_val, (int, float, str))
                            else 5.0
                        )
                    except Exception:
                        retry_after = 5.0

                    # Trigger Global Backoff
                    await self.rate_limiter.trigger_backoff(retry_after)

                    return CheckResult(
                        username=username,
                        status=CheckStatus.RATE_LIMITED,
                        message=f"Rate limited, pausing for {retry_after}s",
                    )

                if response.status_code in (401, 403):
                    return CheckResult(
                        username=username,
                        status=CheckStatus.ERROR,
                        message="Unauthorized (Check Token)",
                    )

                if response.status_code != 200:
                    return CheckResult(
                        username=username,
                        status=CheckStatus.ERROR,
                        message=f"HTTP {response.status_code}",
                    )

                success_data = cast(dict[str, object], response.json())  # type: ignore

                if success_data.get("taken"):
                    return CheckResult(
                        username=username,
                        status=CheckStatus.TAKEN,
                        message="Taken",
                    )
                else:
                    # "taken": false (or missing) means available!
                    self.valid_usernames.append(username)
                    await self.send_webhook(session, username)
                    return CheckResult(
                        username=username,
                        status=CheckStatus.AVAILABLE,
                        message="Available!",
                    )

            except Exception as e:
                logger.error(f"Error checking {username}: {e}")
                return CheckResult(
                    username=username, status=CheckStatus.ERROR, message=str(e)
                )

    async def send_webhook(self, session: AsyncSession, username: str):
        if not self.config.webhook_url:
            return

        embed = WebhookEmbed(
            title=f"**{username}**",
            description="Username is available!",
            color=0x00FF00,
        )
        payload = WebhookPayload(embeds=[embed])

        try:
            # Pydantic HttpUrl needs str() conversion
            # curl_cffi supports json parameter
            _ = await session.post(
                str(self.config.webhook_url), json=payload.model_dump()
            )  # type: ignore
        except Exception as e:
            logger.error(f"Failed to send webhook for {username}: {e}")

    async def process_usernames(self, usernames: list[str]) -> list[CheckResult]:
        # Using AsyncSession with impersonate='chrome'
        async with AsyncSession(impersonate="chrome") as session:
            tasks = [self.check_username(session, user) for user in usernames]
            results = await asyncio.gather(*tasks)
            return results
