"""Tiny JSON-backed store for subscriber chat_ids and last-seen news GUIDs."""
import json
import os
import threading

_DIR = os.path.dirname(os.path.abspath(__file__))
SUBS_FILE = os.path.join(_DIR, "subscribers.json")
_lock = threading.Lock()


def _load():
    if not os.path.exists(SUBS_FILE):
        return {"subscribers": [], "last_news": {}}
    try:
        with open(SUBS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"subscribers": [], "last_news": {}}
    data.setdefault("subscribers", [])
    data.setdefault("last_news", {})
    return data


def _save(data):
    tmp = SUBS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, SUBS_FILE)


def add_subscriber(chat_id):
    """Returns True if newly added."""
    with _lock:
        data = _load()
        if chat_id not in data["subscribers"]:
            data["subscribers"].append(chat_id)
            _save(data)
            return True
        return False


def get_subscribers():
    with _lock:
        return list(_load().get("subscribers", []))


def get_last_news(key):
    with _lock:
        return _load().get("last_news", {}).get(key)


def set_last_news(key, guid):
    with _lock:
        data = _load()
        data["last_news"][key] = guid
        _save(data)
