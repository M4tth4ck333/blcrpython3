# The MIT License
#
# Copyright (c) 2013 Sebastian Ramacher
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# bpdb/__main__.py

import argparse
import logging
import sqlite3
import sys
from contextlib import contextmanager

DB_FILE = "bpdb.sqlite3"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                start_time TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                event_type TEXT,
                details TEXT,
                timestamp TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)
        logging.info("Database initialized.")

def add_session(name):
    from datetime import datetime
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO sessions (name, start_time) VALUES (?, ?)", (name, datetime.utcnow().isoformat()))
        logging.info(f"Added session '{name}'")

def main():
    parser = argparse.ArgumentParser(description="bpdb - Offensive Security DB CLI")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database")
    parser.add_argument("--add-session", type=str, help="Add a new session by name")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.init_db:
        init_db()
        print("Database initialized.")
        sys.exit(0)

    if args.add_session:
        add_session(args.add_session)
        print(f"Session '{args.add_session}' added.")
        sys.exit(0)

    parser.print_help()

if __name__ == "__main__":
    main()
