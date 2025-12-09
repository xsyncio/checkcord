"""Tests for checkcord package."""

import pytest


class TestImports:
    """Test that all modules can be imported correctly."""

    def test_import_main_package(self):
        import checkcord

        assert hasattr(checkcord, "__version__")
        assert checkcord.__version__ == "0.1.0"

    def test_import_checker(self):
        from checkcord import DiscordChecker

        assert DiscordChecker is not None

    def test_import_generators(self):
        from checkcord import (
            RandomCharGenerator,
            DictionaryGenerator,
            LeetGenerator,
            PatternGenerator,
        )

        assert RandomCharGenerator is not None
        assert DictionaryGenerator is not None
        assert LeetGenerator is not None
        assert PatternGenerator is not None

    def test_import_models(self):
        from checkcord import CheckResult, CheckStatus, AppConfig

        assert CheckResult is not None
        assert CheckStatus is not None
        assert AppConfig is not None

    def test_import_ratelimiter(self):
        from checkcord import GlobalRateLimiter

        assert GlobalRateLimiter is not None
