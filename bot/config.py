import json
import os

from pathlib import Path


def load_config(config_path: str = "config.json") -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Override token by env var if provided
    token = os.getenv("BOT_TOKEN") or data.get("bot_token")
    if not token:
        raise ValueError("Bot token must be set in config.json or BOT_TOKEN env var")
    data["bot_token"] = token
    return data