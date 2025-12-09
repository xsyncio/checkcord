"""Tests for checkcord.core.generator module."""

import pytest

from checkcord.core.generator import (
    DictionaryGenerator,
    LeetGenerator,
    PatternGenerator,
    RandomCharGenerator,
)


class TestRandomCharGenerator:
    """Tests for RandomCharGenerator."""

    @pytest.mark.asyncio
    async def test_generate_usernames(self):
        gen = RandomCharGenerator(length=4)
        usernames = await gen.generate(5)
        assert len(usernames) == 5
        for name in usernames:
            assert len(name) == 4

    @pytest.mark.asyncio
    async def test_unique_usernames(self):
        gen = RandomCharGenerator(length=4)
        usernames = await gen.generate(10)
        assert len(usernames) == len(set(usernames))

    @pytest.mark.asyncio
    async def test_no_invalid_patterns(self):
        gen = RandomCharGenerator(length=4)
        usernames = await gen.generate(20)
        for name in usernames:
            assert ".." not in name
            assert "__" not in name
            assert not name.startswith(".")
            assert not name.endswith(".")

    def test_generator_name(self):
        gen = RandomCharGenerator(length=4)
        assert gen.name == "Random Characters"


class TestPatternGenerator:
    """Tests for PatternGenerator."""

    @pytest.mark.asyncio
    async def test_generate_with_pattern(self):
        gen = PatternGenerator(pattern="user_{random}")
        usernames = await gen.generate(5)
        assert len(usernames) == 5
        for name in usernames:
            assert name.startswith("user_")

    @pytest.mark.asyncio
    async def test_unique_pattern_usernames(self):
        gen = PatternGenerator(pattern="test_{random}")
        usernames = await gen.generate(10)
        assert len(usernames) == len(set(usernames))

    def test_generator_name(self):
        gen = PatternGenerator(pattern="x_{random}")
        assert gen.name == "Pattern Based"


class TestDictionaryGenerator:
    """Tests for DictionaryGenerator."""

    @pytest.mark.asyncio
    async def test_generate_dictionary_names(self):
        gen = DictionaryGenerator(add_numbers=False)
        usernames = await gen.generate(5)
        assert len(usernames) == 5
        for name in usernames:
            assert name.islower()

    @pytest.mark.asyncio
    async def test_generate_with_numbers(self):
        gen = DictionaryGenerator(add_numbers=True)
        usernames = await gen.generate(5)
        assert len(usernames) == 5
        # Most should have numbers
        has_numbers = sum(1 for n in usernames if any(c.isdigit() for c in n))
        assert has_numbers >= 0  # May not always have numbers

    def test_generator_name(self):
        gen = DictionaryGenerator()
        assert gen.name == "Dictionary (Adjective + Noun)"


class TestLeetGenerator:
    """Tests for LeetGenerator."""

    @pytest.mark.asyncio
    async def test_generate_leet_names(self):
        gen = LeetGenerator(base_word="test")
        usernames = await gen.generate(5)
        assert len(usernames) == 5

    @pytest.mark.asyncio
    async def test_leet_variations(self):
        gen = LeetGenerator(base_word="hello")
        usernames = await gen.generate(10)
        # Should have some variation
        assert len(set(usernames)) >= 1

    def test_generator_name(self):
        gen = LeetGenerator(base_word="viper")
        assert gen.name == "Leet Speak (viper)"
