from collections import OrderedDict
from datetime import datetime, timedelta

MAX_SESSIONS = 1000
SESSION_TTL = timedelta(hours=24)


class SessionMemory:
    def __init__(self):
        self._sessions = OrderedDict()
        self._timestamps = {}

    def _evict(self):
        now = datetime.now()
        stale = [sid for sid, ts in self._timestamps.items()
                 if now - ts > SESSION_TTL]
        for sid in stale:
            self._sessions.pop(sid, None)
            self._timestamps.pop(sid, None)

        while len(self._sessions) > MAX_SESSIONS:
            sid, _ = self._sessions.popitem(last=False)
            self._timestamps.pop(sid, None)

    def get(self, session_id, default=None):
        self._evict()
        self._timestamps[session_id] = datetime.now()
        return self._sessions.get(session_id, default)

    def set(self, session_id, value):
        self._evict()
        self._sessions[session_id] = value
        self._timestamps[session_id] = datetime.now()

    def delete(self, session_id):
        self._sessions.pop(session_id, None)
        self._timestamps.pop(session_id, None)

    def __contains__(self, session_id):
        self._evict()
        return session_id in self._sessions

    def __getitem__(self, session_id):
        self._evict()
        self._timestamps[session_id] = datetime.now()
        return self._sessions[session_id]

    def __setitem__(self, session_id, value):
        self._evict()
        self._sessions[session_id] = value
        self._timestamps[session_id] = datetime.now()

    def __delitem__(self, session_id):
        self._sessions.pop(session_id, None)
        self._timestamps.pop(session_id, None)


conversation_memory = SessionMemory()


def add_message(session_id, role, content):
    history = conversation_memory.get(session_id, [])
    history.append({"role": role, "content": content})
    conversation_memory.set(session_id, history)


def get_history(session_id):
    return conversation_memory.get(session_id, [])
