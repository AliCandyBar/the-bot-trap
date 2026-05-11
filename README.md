# The Bot Trap

A small [Discord.py](https://discordpy.readthedocs.io/) moderation helper that watches for Discord invite links in server messages. When someone posts an invite, the bot **timeouts** them for one hour, **purges** their recent messages in that channel (up to 50), and sends a **review card** to a dedicated moderation channel where staff can **ban** or **unmute** with one click.

Useful for slowing automated spam and giving moderators a clear, actionable queue instead of chasing invites across channels.

## What it does

| Step | Behavior |
|------|----------|
| Detection | Normalizes message text and flags patterns that look like `discord.gg/...` or `discord.com/invite/...`, including common obfuscation with punctuation. |
| Automatic action | 1-hour timeout on the author; purge up to 50 of their messages in the channel where the invite was posted. |
| Review | Posts an embed (plus the raw message text) to a channel named **`the-bot-trap`**. |
| Moderator controls | **Ban** — bans the user (deletes their messages from the last 7 days server-wide per Discord’s ban behavior). **Unmute** — clears the timeout. Buttons disable after use. |

Bots and DMs are ignored. Messages outside a guild are ignored.

## Requirements

- **Python 3** (3.10+ recommended; match what your `discord.py` version supports)
- A Discord **application** and **bot** with a token
- Bot **permissions** on the server (see below)

Dependencies are listed in `requirements.txt` (including `discord.py` and `python-dotenv` for loading `.env`).

## Discord setup

### Privileged intents

In the [Discord Developer Portal](https://discord.com/developers/applications) → your app → **Bot**, enable:

- **Message Content Intent** — required so the bot can read message text and detect invites.
- **Server Members Intent** — used for member lookups (timeouts, ban/unmute flow).

### Invite URL

Invite the bot with permissions that allow it to:

- Read messages / view channels
- Send messages and embeds
- Manage messages (purge)
- Moderate members (timeout)
- Ban members (for the Ban button)

You can use the permission calculator in the Developer Portal or an invite URL generator with the appropriate bitwise permission flags for your server’s needs.

### Moderation channel

Create a **text channel** whose name is exactly:

```text
the-bot-trap
```

Review embeds are sent only to that channel. If the channel does not exist, the bot may error when handling an invite—create it before relying on the bot in production.

## Installation

```bash
git clone https://github.com/AliCandyBar/the-bot-trap.git
cd the-bot-trap
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

### Bot token (`DISCORD_TOKEN`)

The bot reads **`DISCORD_TOKEN`** from the environment. With [python-dotenv](https://pypi.org/project/python-dotenv/), `bot-trap.py` loads a **`.env`** file in the project root so you do not need to export variables manually for local runs.

1. Copy the example file (committed in this repo):

   ```bash
   cp .env_example .env   # Windows: copy .env_example .env
   ```

2. Edit **`.env`** and set your token (no quotes needed unless your shell requires them):

   ```env
   DISCORD_TOKEN=<your bot token from the Discord Developer Portal>
   ```

The **`.env_example`** file in the repository shows the variable name only; it is safe to commit. **`.env`** is gitignored—never commit a real token. For production you can set `DISCORD_TOKEN` in your host’s environment or secrets manager instead of using a `.env` file.

### Exempt roles

Staff or trusted roles can be skipped by the scanner. In `bot-trap.py`, set `exempt` to a set of **role IDs** (integers):

```python
exempt = {123456789012345678, 987654321098765432}
```

Leave `exempt = {}` if no roles should bypass detection.

### Command prefix

Commands use the prefix **`~`** (tilde), e.g. `~ping`.

### Optional: embed appearance

The review embed title uses a **custom animated emoji** from a specific server. If that emoji is not available in your server, Discord may show a broken or generic placeholder. Edit the `title=` string in the `discord.Embed` in `bot-trap.py` to use your own emoji or plain text.

## Usage

```bash
python bot-trap.py
```

With the bot running and invited to your server:

- Posting a Discord invite in a normal text channel triggers timeout + purge + review message (unless exempt).
- Moderators use **Ban** or **Unmute** on the review message in `#the-bot-trap`.
- `~ping` replies with a simple online check.

## Limitations

- Invite detection is heuristic (stripped/lowercased text); unusual URL shorteners or novel obfuscation may not match.
- Purge is limited to **50** messages in the **current channel** and only from the offending user.
- The review channel name is **hardcoded** to `the-bot-trap`.
