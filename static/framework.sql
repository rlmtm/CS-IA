CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    auto_generated BOOLEAN
);

CREATE TABLE IF NOT EXISTS conversations (
    convo_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    topic TEXT,
    language TEXT,
    date,
    length INTEGER
);