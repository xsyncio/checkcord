import asyncio
from typing import cast

from curl_cffi.requests import AsyncSession, Response

from checkcord.core.config import load_config

# This seems to be the endpoint used by the client for checking validity
URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"


async def debug_pomelo():
    config = load_config()
    print(f"Token: {config.token[:5]}...")

    headers = {
        "Authorization": config.token,
        "Content-Type": "application/json",
    }

    # Test with 'ivpa' which we know is taken
    username = "ivpa"
    payload = {"username": username}

    async with AsyncSession(impersonate="chrome") as session:
        print(f"Checking {username} with POMELO endpoint...")
        response: Response = await session.post(URL, headers=headers, json=payload)  # type: ignore
        print(f"Status: {response.status_code}")
        try:
            # json() has partially unknown return type in stubs
            data = cast(dict[str, object], response.json())  # type: ignore
            print("Response JSON:")
            import json

            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Text: {response.text}")


if __name__ == "__main__":
    asyncio.run(debug_pomelo())
