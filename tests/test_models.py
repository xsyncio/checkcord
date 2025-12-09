"""Tests for checkcord.models module."""

import pytest
from checkcord.models import (
    AppConfig,
    CheckResult,
    CheckStatus,
    WebhookEmbed,
    WebhookEmbedFooter,
    WebhookPayload,
)


class TestCheckStatus:
    """Tests for CheckStatus enum."""

    def test_available_status(self):
        assert CheckStatus.AVAILABLE == "AVAILABLE"

    def test_taken_status(self):
        assert CheckStatus.TAKEN == "TAKEN"

    def test_rate_limited_status(self):
        assert CheckStatus.RATE_LIMITED == "RATE_LIMITED"

    def test_error_status(self):
        assert CheckStatus.ERROR == "ERROR"


class TestCheckResult:
    """Tests for CheckResult model."""

    def test_create_result(self):
        result = CheckResult(
            username="testuser",
            status=CheckStatus.AVAILABLE,
            message="Username is available",
        )
        assert result.username == "testuser"
        assert result.status == CheckStatus.AVAILABLE
        assert result.message == "Username is available"

    def test_result_without_message(self):
        result = CheckResult(username="test", status=CheckStatus.TAKEN)
        assert result.message is None


class TestAppConfig:
    """Tests for AppConfig model."""

    def test_create_config(self):
        config = AppConfig(token="test_token")
        assert config.token == "test_token"
        assert config.thread_count == 5
        assert config.retry_delay == 2.0
        assert config.webhook_url is None

    def test_config_with_custom_values(self):
        config = AppConfig(
            token="my_token",
            thread_count=10,
            retry_delay=5.0,
        )
        assert config.thread_count == 10
        assert config.retry_delay == 5.0


class TestWebhookModels:
    """Tests for webhook-related models."""

    def test_webhook_embed_footer(self):
        footer = WebhookEmbedFooter()
        assert footer.text == "CheckCord"

    def test_webhook_embed(self):
        embed = WebhookEmbed(title="Test Title")
        assert embed.title == "Test Title"
        assert embed.color == 706405
        assert embed.footer.text == "CheckCord"

    def test_webhook_payload(self):
        embed = WebhookEmbed(title="Found!", description="Username available")
        payload = WebhookPayload(embeds=[embed])
        assert len(payload.embeds) == 1
        assert payload.content is None
