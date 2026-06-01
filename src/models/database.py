"""
Database module.
Handles local SQLite3 database operations for storing 
historical feedback and transcripts.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.getcwd(), 'history.db'))

def init_db():
    """Initializes the database and creates the history table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            transcription TEXT NOT NULL,
            feedback TEXT NOT NULL
        )
    ''')
    
    # Migrate existing database seamlessly
    try:
        cursor.execute("ALTER TABLE history ADD COLUMN wpm REAL DEFAULT 0")
        cursor.execute("ALTER TABLE history ADD COLUMN filler_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Columns already exist
        
    try:
        cursor.execute("ALTER TABLE history ADD COLUMN topic TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def insert_history(transcription, feedback, wpm=0.0, filler_count=0, topic=None):
    """Inserts a new transcription and feedback entry into the database. Returns the new row ID and timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO history (timestamp, transcription, feedback, wpm, filler_count, topic)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, transcription, feedback, wpm, filler_count, topic))
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id, timestamp

def get_all_history():
    """Retrieves all history records from the database, ordered by newest first."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, timestamp, transcription, feedback, wpm, filler_count, topic 
        FROM history 
        ORDER BY id DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    # Return as list of dicts for easier consumption
    return [
        {"id": row[0], "timestamp": row[1], "transcription": row[2], "feedback": row[3], "wpm": row[4], "filler_count": row[5], "topic": row[6]}
        for row in rows
    ]

def get_history_by_id(record_id):
    """Retrieves a single history record by its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, timestamp, transcription, feedback, wpm, filler_count, topic 
        FROM history 
        WHERE id = ?
    ''', (record_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"id": row[0], "timestamp": row[1], "transcription": row[2], "feedback": row[3], "wpm": row[4], "filler_count": row[5], "topic": row[6]}
    return None
