CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, email TEXT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS session (
    user_id INTEGER NOT NULL,
    title TEXT,
    language,
    date TEXT,
    length INTEGER,
    recording_id INTEGER
);