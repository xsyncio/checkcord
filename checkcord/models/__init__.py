from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class WebhookEmbedFooter(BaseModel):
    text: str = "CheckCord"


class WebhookEmbed(BaseModel):
    title: str
    description: str | None = None
    url: str | None = "https://github.com/xsyncio/CheckCord"
    color: int = 706405
    footer: WebhookEmbedFooter = Field(default_factory=WebhookEmbedFooter)
    timestamp: str = Field(default_factory=lambda: str(datetime.now()))


class WebhookPayload(BaseModel):
    embeds: list[WebhookEmbed]
    content: str | None = None


class AppConfig(BaseModel):
    token: str = Field(..., description="Discord User Token")
    webhook_url: HttpUrl | None = Field(
        None, description="Discord Webhook URL for notifications"
    )
    thread_count: int = Field(5, ge=1, le=50, description="Number of concurrent checks")
    retry_delay: float = Field(
        2.0, ge=0.0, description="Delay between checks in seconds"
    )


class CheckStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    TAKEN = "TAKEN"
    RATE_LIMITED = "RATE_LIMITED"
    ERROR = "ERROR"


class CheckResult(BaseModel):
    username: str
    status: CheckStatus
    message: str | None = None
