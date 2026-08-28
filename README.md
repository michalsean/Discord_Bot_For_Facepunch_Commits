# Rust Commit Discord Tracker Bot

A lightweight, automated Discord bot built with `discord.py` and `aiohttp` that tracks and posts real-time Facepunch Rust commit logs (`rust_reboot` main branch) directly into your Discord channel with styled diff embeds.

**Author:** Michal Okapiec  
**Source Data:** [commits.facepunch.com](https://commits.facepunch.com)

---

## Features

- **Automated Polling**: Fetches the latest Rust development commits every 60 seconds.
- **Rich Discord Embeds**: Formats commit descriptions with `diff` syntax highlighting, author names, avatars, branch metadata, and direct web links.
- **State Persistence**: Saves the last announced commit ID in a local `last.json` file to prevent duplicate messages across script restarts.
- **First-Run Backfill**: Posts the 5 most recent commits on initial setup so your channel isn't empty.
- **Text Cleaning**: Sanitizes incoming commit text to avoid character encoding issues and broken embeds.

---

## Requirements and Dependencies

- **Python 3.8+**
- Python Libraries:
  - `discord.py`
  - `aiohttp`

### Installation

Install the required Python modules via `pip`:

```bash
pip install discord.py aiohttp
```

---

## Configuration Setup

Open the main script file (`bot.py`) and update the configuration variables at the top of the file:

```python
TOKEN = "YOUR_BOT_TOKEN_HERE"      # Replace with your Discord Bot Token
CHANNEL_ID = 123456789012345678     # Replace with your target Discord Channel ID (Integer)
```

> **Note**: Ensure `CHANNEL_ID` is an integer (e.g. `1234567890`), not a string starting with `#`.

### Required Discord Bot Permissions
Your bot requires the following permissions in your server/channel:
- **Read Messages / View Channel**
- **Send Messages**
- **Embed Links**

---

## Running the Bot

### Standard Launch

```bash
python bot.py
```

### Windows Command Prompt Launch

If you are running the bot from a specific folder or using a dedicated Python executable, use the following template:

```cmd
cd /d "C:\Path\To\Your\Bot\Folder"
"C:\Path\To\Python\python.exe" bot.py
```

---

## Project Structure

```text
├── bot.py         # Main bot script containing fetching and Discord logic
├── last.json      # Auto-generated file tracking the latest posted commit ID
└── README.md      # Project documentation
```

---

## How It Works

1. **Bot Startup**: Upon logging into Discord (`on_ready`), the bot starts an asynchronous background task loop (`check_loop`).
2. **API Fetch**: Queries `https://commits.facepunch.com/r/rust_reboot/main?format=json` for JSON commit data.
3. **Commit Checking**:
   - Reads `last.json` for state history.
   - On **first run**, posts the 5 latest commits and writes the newest commit ID to `last.json`.
   - On **subsequent runs**, identifies any commits published since `last.json` was updated, posts them in chronological order, and updates `last.json`.
4. **Embed Delivery**: Formats the commit message with diff syntax (`+ message`), attaches author metadata, and posts to the configured channel.
5. **Sleep Cycle**: Waits 60 seconds (`CHECK_INTERVAL`) before repeating.

---

## License and Credits

- **Developer**: Michal Okapiec
- **Data Source**: Facepunch Commits (`commits.facepunch.com`)
