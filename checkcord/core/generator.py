import random
import string
from abc import ABC, abstractmethod
from typing import cast, override

from rich.console import Console

console = Console()


class GeneratorStrategy(ABC):
    def __init__(self):
        self.seen: set[str] = set()

    @abstractmethod
    async def generate(self, count: int) -> list[str]:
        """Generate a list of usernames."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Friendly name of the generator."""
        pass


class RandomCharGenerator(GeneratorStrategy):
    def __init__(self, length: int = 4, dictionary_mode: bool = False):
        super().__init__()
        self.length: int = length
        self.dictionary_mode: bool = dictionary_mode  # Placeholder for future

    @property
    @override
    def name(self) -> str:
        return "Random Characters"

    @override
    async def generate(self, count: int) -> list[str]:
        usernames: list[str] = []
        chars = string.ascii_lowercase + "._"
        attempts = 0
        max_attempts = count * 50  # Avoid infinite loops

        while len(usernames) < count and attempts < max_attempts:
            attempts += 1
            name = "".join(random.choices(chars, k=self.length))

            # Basic validation
            if (
                ".." in name
                or "__" in name
                or name.startswith(".")
                or name.endswith(".")
            ):
                continue

            if name in self.seen:
                continue

            self.seen.add(name)
            usernames.append(name)

        if len(usernames) < count:
            console.print(
                f"[yellow]Warning: Could only generate {len(usernames)} unique names (Pool exhausted?)[/yellow]"
            )

        return usernames


class RemoteListGenerator(GeneratorStrategy):
    def __init__(
        self,
        url: str = "",  # No default, user must provide URL
    ):
        super().__init__()
        self.url: str = url

    @property
    @override
    def name(self) -> str:
        return "Remote Wordlist (Xsyncio Gist)"

    @override
    async def generate(self, count: int) -> list[str]:
        try:
            from curl_cffi.requests import AsyncSession, Response

            async with AsyncSession(impersonate="chrome") as session:
                response: Response = await session.get(self.url)  # type: ignore
                if response.status_code != 200:
                    console.print(
                        f"[red]Failed to fetch wordlist: {response.status_code}[/red]"
                    )
                    return []
                text = response.text

                import ast
                # from typing import Any  <-- removed

                all_names: list[str] = []
                try:
                    # literal_eval return type is Any, but we expect list.
                    # Explicit cast or check to satisfy strict mode
                    parsed: object = ast.literal_eval(text)
                    if isinstance(parsed, list):
                        # Help strict mode understand the list content
                        parsed_list = cast(list[object], parsed)
                        all_names = [str(x) for x in parsed_list]
                    else:
                        raise ValueError("Not a list")
                except Exception:
                    # Fallback to line based
                    all_names = [
                        line.strip() for line in text.splitlines() if line.strip()
                    ]

            random.shuffle(all_names)
            return all_names[:count]

        except Exception as e:
            console.print(f"[red]Error fetching remote list: {e}[/red]")
            return []


class PatternGenerator(GeneratorStrategy):
    def __init__(self, pattern: str = "user_{random}"):
        super().__init__()
        self.pattern: str = pattern

    @property
    @override
    def name(self) -> str:
        return "Pattern Based"

    @override
    async def generate(self, count: int) -> list[str]:
        usernames: list[str] = []
        chars = string.ascii_lowercase + "0123456789"
        attempts = 0
        max_attempts = count * 50

        while len(usernames) < count and attempts < max_attempts:
            attempts += 1
            rand_str = "".join(random.choices(chars, k=4))
            name = self.pattern.replace("{random}", rand_str)

            if name in self.seen:
                continue

            self.seen.add(name)
            usernames.append(name)

        if len(usernames) < count:
            console.print(
                f"[yellow]Warning: Could only generate {len(usernames)} unique names[/yellow]"
            )

        return usernames


class DictionaryGenerator(GeneratorStrategy):
    def __init__(self, add_numbers: bool = False):
        super().__init__()
        self.add_numbers: bool = add_numbers
        self.adjectives: list[str] = [
            "Cool",
            "Happy",
            "Red",
            "Blue",
            "Dark",
            "Light",
            "Fast",
            "Super",
            "Hyper",
            "Mega",
            "Ultra",
            "Neon",
            "Cyber",
            "Tech",
            "Pro",
            "Elite",
            "Master",
            "Shadow",
            "Ghost",
            "Iron",
            "Gold",
            "Silver",
        ]
        self.nouns: list[str] = [
            "Tiger",
            "Bear",
            "Dragon",
            "Wolf",
            "Lion",
            "Eagle",
            "Shark",
            "Bot",
            "Droid",
            "Cyborg",
            "Ninja",
            "Samurai",
            "Knight",
            "Wizard",
            "Titan",
            "Ranger",
            "Pilot",
            "Gamer",
            "Coder",
            "Hacker",
            "Viper",
            "Cobra",
        ]

    @property
    @override
    def name(self) -> str:
        return "Dictionary (Adjective + Noun)"

    @override
    async def generate(self, count: int) -> list[str]:
        usernames: list[str] = []
        attempts = 0
        max_attempts = count * 50

        while len(usernames) < count and attempts < max_attempts:
            attempts += 1
            adj = random.choice(self.adjectives)
            noun = random.choice(self.nouns)
            name = f"{adj}{noun}"

            if self.add_numbers:
                name += str(random.randint(0, 999))

            name = name.lower()  # Discord usernames are lowercase

            if name in self.seen:
                continue

            self.seen.add(name)
            usernames.append(name)

        if len(usernames) < count:
            console.print(
                f"[yellow]Warning: Could only generate {len(usernames)} unique names[/yellow]"
            )

        return usernames


class LeetGenerator(GeneratorStrategy):
    def __init__(self, base_word: str):
        super().__init__()
        self.base_word: str = base_word
        self.subs: dict[str, list[str]] = {
            "a": ["4", "@"],
            "e": ["3"],
            "i": ["1", "!"],
            "o": ["0"],
            "s": ["5", "$"],
            "t": ["7"],
            "l": ["1"],
            "b": ["8"],
        }

    @property
    @override
    def name(self) -> str:
        return f"Leet Speak ({self.base_word})"

    @override
    async def generate(self, count: int) -> list[str]:
        usernames: list[str] = []
        attempts = 0
        max_attempts = count * 100

        while len(usernames) < count and attempts < max_attempts:
            attempts += 1
            # Simple probabilistic substitution
            name_chars: list[str] = []
            for char in self.base_word.lower():
                if (
                    char in self.subs and random.random() > 0.3
                ):  # 70% chance to substitute
                    name_chars.append(random.choice(self.subs[char]))
                else:
                    name_chars.append(char)

            name = "".join(name_chars)

            if name in self.seen:
                continue

            self.seen.add(name)
            usernames.append(name)

        if len(usernames) < count:
            console.print(
                f"[yellow]Warning: Could only generate {len(usernames)} unique names[/yellow]"
            )

        return usernames
