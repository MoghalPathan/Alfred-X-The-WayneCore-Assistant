"""
AlfredX: Memory System v2.2 — pure JSON storage
All user data (facts, conversations, tasks) is stored in human-readable
JSON files on the user's own computer. No database, no server.
Public API is identical to the old SQLite version.
"""
import json
import os
import threading
from datetime import datetime
from config import DATA_DIR

_MEMORY_FILE = os.path.join(DATA_DIR, "alfred_memory.json")
_lock = threading.Lock()


def _now():
    return datetime.now().isoformat()


def _load():
    if not os.path.exists(_MEMORY_FILE):
        return {"facts": [], "conversations": [], "tasks": [], "next_id": 1}
    try:
        with open(_MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Memory] Corrupt memory file, starting fresh: {e}")
        try:
            os.replace(_MEMORY_FILE, _MEMORY_FILE + ".corrupt")
        except Exception:
            pass
        return {"facts": [], "conversations": [], "tasks": [], "next_id": 1}
    data.setdefault("facts", [])
    data.setdefault("conversations", [])
    data.setdefault("tasks", [])
    data.setdefault("next_id", 1)
    return data


def _save(data):
    tmp = _MEMORY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, _MEMORY_FILE)  # atomic write: never leaves a half-saved file


class Memory:
    """Persistent memory — remembers user facts, conversations, and tasks in JSON."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"[Memory] [OK] JSON memory ready: {_MEMORY_FILE}")

    # --- Facts ---
    def remember(self, category, key, value):
        with _lock:
            data = _load()
            for fact in data["facts"]:
                if fact["category"] == category and fact["key"] == key:
                    fact["value"] = str(value)
                    fact["updated_at"] = _now()
                    break
            else:
                data["facts"].append({
                    "category": category, "key": key, "value": str(value),
                    "updated_at": _now(),
                })
            _save(data)
        print(f"[Memory] Saved {category}/{key} = {value}")

    def recall(self, category=None, key=None):
        with _lock:
            data = _load()
        if category and key:
            for fact in data["facts"]:
                if fact["category"] == category and fact["key"] == key:
                    return fact["value"]
            return None
        elif category:
            return {f["key"]: f["value"] for f in data["facts"] if f["category"] == category}
        else:
            return [
                {"category": f["category"], "key": f["key"], "value": f["value"]}
                for f in data["facts"]
            ]

    def get_all_facts(self):
        return self.recall()

    def forget(self, category, key):
        with _lock:
            data = _load()
            before = len(data["facts"])
            data["facts"] = [
                f for f in data["facts"]
                if not (f["category"] == category and f["key"] == key)
            ]
            removed = before - len(data["facts"])
            _save(data)
        if removed:
            print(f"[Memory] Forgot: {category}/{key}")

    # --- Conversations ---
    def log_message(self, role, content, language="en"):
        with _lock:
            data = _load()
            data["conversations"].append({
                "role": role, "content": content,
                "language": language, "timestamp": _now(),
            })
            if len(data["conversations"]) > 500:
                data["conversations"] = data["conversations"][-500:]
            _save(data)

    def get_recent_conversations(self, limit=10):
        with _lock:
            data = _load()
        return [
            {"role": c["role"], "content": c["content"], "timestamp": c["timestamp"]}
            for c in data["conversations"][-limit:]
        ]

    def search_conversations(self, query):
        with _lock:
            data = _load()
        q = query.lower()
        return [
            {"role": c["role"], "content": c["content"], "timestamp": c["timestamp"]}
            for c in reversed(data["conversations"])
            if q in c["content"].lower()
        ][:20]

    # --- Tasks ---
    def add_task(self, title, description=""):
        with _lock:
            data = _load()
            task_id = data["next_id"]
            data["next_id"] += 1
            data["tasks"].append({
                "id": task_id, "title": title, "description": description,
                "status": "pending", "created_at": _now(), "completed_at": None,
            })
            _save(data)
        print(f"[Memory] Task added: {title}")
        return task_id

    def complete_task(self, task_id):
        with _lock:
            data = _load()
            for task in data["tasks"]:
                if task["id"] == task_id:
                    task["status"] = "completed"
                    task["completed_at"] = _now()
                    break
            _save(data)

    def get_tasks(self, status="pending"):
        with _lock:
            data = _load()
        return [
            {"id": t["id"], "title": t["title"], "description": t["description"],
             "status": t["status"], "created": t["created_at"]}
            for t in reversed(data["tasks"])
            if t["status"] == status
        ]