import json
from pathlib import Path
from typing import Any

from checkcord.models import AppConfig

CONFIG_FILE = Path("config.json")


def load_config() -> AppConfig:
    if not CONFIG_FILE.exists():
        # Create default config if it doesn't exist
        default_config = AppConfig(
            token="YOUR_TOKEN_HERE", webhook_url=None, thread_count=5, retry_delay=2.0
        )
        save_config(default_config)
        return default_config

    try:
        with open(CONFIG_FILE) as f:
            data: dict[str, Any] = json.load(f)  # type: ignore
            # Handle empty Webhook string effectively
            if "webhook_url" in data and not data["webhook_url"]:
                data["webhook_url"] = None
            return AppConfig(**data)
    except Exception as e:
        print(f"Error loading config: {e}")
        return AppConfig(
            token="INVALID_TOKEN_LOAD_FAILED",
            webhook_url=None,
            thread_count=5,
            retry_delay=2.0,
        )


def save_config(config: AppConfig):
    with open(CONFIG_FILE, "w") as f:
        f.write(config.model_dump_json(indent=4))
