import sqlite3
from typing import List, Dict, Optional

DB_NAME = "chat_history.db"


def get_connection():
    """Returns a SQLite connection to the chat history database."""
    return sqlite3.connect(DB_NAME)


def init_db():
    """
    Creates the SQLite database tables (chat_sessions, messages, improvement_notes)
    and automatically migrates older single-session tables without losing data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Table for Chat Sessions (like ChatGPT sidebar threads)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Table for Messages linked to a specific chat_session
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
    """)

    # Automatic schema migration if 'messages' was created in an earlier phase without 'session_id'
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    if "session_id" not in columns:
        cursor.execute("ALTER TABLE messages ADD COLUMN session_id INTEGER")
        # Check if there are existing messages from Phase 2 and group them into an initial session
        cursor.execute("SELECT COUNT(*) FROM messages WHERE session_id IS NULL")
        orphan_count = cursor.fetchone()[0]
        if orphan_count > 0:
            cursor.execute(
                "INSERT INTO chat_sessions (title) VALUES (?)",
                ("Previous Chat History",)
            )
            legacy_session_id = cursor.lastrowid
            cursor.execute(
                "UPDATE messages SET session_id = ? WHERE session_id IS NULL",
                (legacy_session_id,)
            )

    # 3. Table for Response Improvement Rules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS improvement_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# CHAT SESSION FUNCTIONS (ChatGPT Sidebar)
# ==========================================

def create_chat_session(title: str) -> int:
    """Creates a new chat session with the given title and returns its session_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_sessions (title) VALUES (?)", (title,))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def update_session_title(session_id: int, new_title: str):
    """Updates the title of an existing chat session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chat_sessions SET title = ? WHERE id = ?",
        (new_title, session_id)
    )
    conn.commit()
    conn.close()


def get_all_sessions() -> List[Dict]:
    """Returns all saved chat sessions ordered from newest to oldest."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, created_at FROM chat_sessions ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "created_at": r[2]} for r in rows]


def delete_chat_session(session_id: int):
    """Deletes a chat session and all of its messages from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


# ==========================================
# MESSAGE FUNCTIONS
# ==========================================

def save_message(role: str, content: str, session_id: Optional[int] = None):
    """Saves a user or assistant message into the database under a session_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()


def get_session_messages(session_id: int, limit: int = 50) -> List[Dict]:
    """Fetches messages belonging to a specific chat session in chronological order."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def get_recent_messages(limit: int = 10) -> List[Dict]:
    """Backward-compatible helper for terminal chatbot.py."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


# ==========================================
# IMPROVEMENT RULES FUNCTIONS (Add & Delete)
# ==========================================

def add_improvement_note(note: str):
    """Saves a new response improvement rule to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO improvement_notes (note) VALUES (?)", (note,))
    conn.commit()
    conn.close()


def get_improvement_notes_with_ids() -> List[Dict]:
    """Returns all saved rules with their database IDs so individual rules can be deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, note FROM improvement_notes ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "note": r[1]} for r in rows]


def get_improvement_notes() -> List[str]:
    """Returns just the list of rule strings for building the system prompt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT note FROM improvement_notes ORDER BY id ASC")
    notes = [r[0] for r in cursor.fetchall()]
    conn.close()
    return notes


def delete_improvement_note(note_id: int):
    """Deletes a single improvement rule by its database ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM improvement_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()