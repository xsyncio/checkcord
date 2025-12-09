import asyncio
from typing import cast

from curl_cffi.requests import AsyncSession

from checkcord.core.config import load_config

URL = "https://discord.com/api/v10/users/@me"


async def debug_check():
    config = load_config()
    print(f"Token: {config.token[:5]}...")

    headers = {
        "Authorization": config.token,
        "Content-Type": "application/json",
    }

    # Test with 'ivpa' which we know is taken but reported as available
    username = "ivpa"
    payload = {"username": username}

    async with AsyncSession(impersonate="chrome") as session:
        print(f"Checking {username}...")
        response = await session.patch(URL, headers=headers, json=payload)  # type: ignore
        print(f"Status: {response.status_code}")

        # Explicit cast to fix strict mode complaint about json() returning Any
        data = cast(dict[str, object], response.json())  # type: ignore
        print("Response JSON:")
        import json

        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    asyncio.run(debug_check())
