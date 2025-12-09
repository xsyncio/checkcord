<div align="center">
  <img src="assets/banner.png" alt="CheckCord Banner" width="100%" />

  # CheckCord

  **A strictly typed, production-grade Discord username availability checker and generator.**

  [![License: MIT](https://img.shields.io/badge/License-MIT-5865F2.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/python-3.10+-5865F2?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
  [![Checked with BasedPyright](https://img.shields.io/badge/checked_with-basedpyright-5865F2?style=for-the-badge)](https://github.com/DetachHead/basedpyright)

</div>

<br />

## ✨ Features

- 🚀 **Blazing Fast**: Engineered with `curl_cffi` for high-performance, async HTTP requests that mimic browser fingerprints.
- 🛡️ **Strictly Typed**: Zero `Any`, zero `type: ignore`. A codebase you can trust, verified by `basedpyright` in strict mode.
- 🧩 **Modular Architecture**: Cleanly separated concerns (`core`, `cli`, `util`) for maximum maintainability.
- 🧠 **Smart Generators**:
  - **Random**: `xc._`
  - **Dictionary**: Cool Adjective + Noun combinations.
  - **Leet Speak**: `v1p3r` style transformations.
  - **Remote**: Fetch wordlists dynamically.
- ⏱️ **Intelligent Rate Limiting**: Global backoff handling that respects Discord's API limits automatically.
- 🔄 **Proxy Rotation**: Just drop a `proxies.txt` file and let CheckCord handle the rotation.
- 🔔 **Webhook Notifications**: Get notified instantly via Discord webhooks when a username is found.

---

## 📦 Installation

```bash
git clone https://github.com/Xsyncio/checkcord.git
cd checkcord
pip install -e .
```

---

## ⚡ Usage

### 🧙 Interactive Wizard

Simply run the tool to enter the interactive mode:
```bash
checkcord
```

### 🖥️ Command Line Interface

**Generate & Check**:
```bash
# Generate 50 usernames of length 4
checkcord generate --count 50 --length 4
```

**Check from File**:
```bash
# Check validity of a list of usernames
checkcord check --file my_usernames.txt
```

---

## ⚙️ Configuration

CheckCord automatically generates a `config.json` on first run.

```json
{
  "token": "YOUR_USER_TOKEN",
  "webhook_url": "YOUR_WEBHOOK_URL",
  "thread_count": 5,
  "retry_delay": 2.5
}
```

> [!WARNING]
> **Use at your own risk.** Automating user accounts may violate Discord Terms of Service.

---

## 🛠️ Development

<div align="center">

| Command | Description |
| :--- | :--- |
| `pytest` | Run the test suite |
| `basedpyright` | Run strict type checking |

</div>

<br />

  <div align="center">
  <sub>Built with ❤️ by Xsyncio</sub>
</div>
