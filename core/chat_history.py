"""
AlfredX v2.2 — Chat History Persistence (JSON)
All chat sessions and messages stored in one JSON file on the user's PC:
    <user data folder>/alfredx_history.json
Public API is identical to the old SQLite version.
"""
import json
import os
import threading
from datetime import datetime
from config import DATA_DIR

HISTORY_FILE = os.path.join(DATA_DIR, "alfredx_history.json")
_lock = threading.Lock()


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load():
    if not os.path.exists(HISTORY_FILE):
        return {"next_session_id": 1, "sessions": []}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ChatHistory] Corrupt history file, starting fresh: {e}")
        try:
            os.replace(HISTORY_FILE, HISTORY_FILE + ".corrupt")
        except Exception:
            pass
        return {"next_session_id": 1, "sessions": []}
    data.setdefault("next_session_id", 1)
    data.setdefault("sessions", [])
    return data


def _save(data):
    tmp = HISTORY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, HISTORY_FILE)  # atomic write


class ChatHistory:
    """Manages chat session persistence using a single JSON file."""

    def __init__(self, db_path=None):
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"[ChatHistory] [OK] JSON history ready: {HISTORY_FILE}")

    @staticmethod
    def _find(data, session_id):
        for s in data["sessions"]:
            if s["id"] == session_id:
                return s
        return None

    # ─── SESSION MANAGEMENT ───────────────────────────────────────
    def create_session(self, name=None):
        if name is None:
            name = f"Chat — {datetime.now().strftime('%b %d, %H:%M')}"
        with _lock:
            data = _load()
            for s in data["sessions"]:
                s["is_last"] = False
            session = {
                "id": data["next_session_id"],
                "name": name,
                "is_last": True,
                "created_at": _now(),
                "updated_at": _now(),
                "messages": [],
            }
            data["next_session_id"] += 1
            data["sessions"].append(session)
            _save(data)
            return session["id"]

    def get_last_session_id(self):
        with _lock:
            data = _load()
        if not data["sessions"]:
            return None
        for s in data["sessions"]:
            if s.get("is_last"):
                return s["id"]
        return data["sessions"][-1]["id"]

    def list_sessions(self, limit=50):
        with _lock:
            data = _load()
        sessions = sorted(data["sessions"], key=lambda s: s["updated_at"], reverse=True)
        return [
            {"id": s["id"], "name": s["name"],
             "created_at": s["created_at"], "updated_at": s["updated_at"]}
            for s in sessions[:limit]
        ]

    def rename_session(self, session_id, new_name):
        with _lock:
            data = _load()
            s = self._find(data, session_id)
            if s:
                s["name"] = new_name
                _save(data)

    def delete_session(self, session_id):
        with _lock:
            data = _load()
            data["sessions"] = [s for s in data["sessions"] if s["id"] != session_id]
            _save(data)

    # ─── MESSAGE MANAGEMENT ───────────────────────────────────────
    def add_message(self, session_id, role, content, metadata=None):
        with _lock:
            data = _load()
            s = self._find(data, session_id)
            if not s:
                return
            s["messages"].append({
                "role": role,
                "content": content,
                "timestamp": _now(),
                "metadata": metadata or {},
            })
            s["updated_at"] = _now()
            if len(s["messages"]) > 1000:
                s["messages"] = s["messages"][-1000:]
            _save(data)

    def get_messages(self, session_id):
        with _lock:
            data = _load()
            s = self._find(data, session_id)
        if not s:
            return []
        return [
            {"role": m["role"], "content": m["content"],
             "timestamp": m["timestamp"], "metadata": m.get("metadata", {})}
            for m in s["messages"]
        ]

    def get_context_messages(self, session_id, limit=20):
        with _lock:
            data = _load()
            s = self._find(data, session_id)
        if not s:
            return []
        return [
            {"role": m["role"], "content": m["content"]}
            for m in s["messages"][-limit:]
        ]

    def clear_session_messages(self, session_id):
        with _lock:
            data = _load()
            s = self._find(data, session_id)
            if s:
                s["messages"] = []
                s["updated_at"] = _now()
                _save(data)

    def get_message_count(self, session_id):
        with _lock:
            data = _load()
            s = self._find(data, session_id)
        return len(s["messages"]) if s else 0


# Module-level singleton, same as before:
chat_db = ChatHistory()