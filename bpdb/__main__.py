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
# blcrpython3/bpdb/__main__.py
import argparse
import logging
import sys
import sqlite3
from datetime import datetime
import importlib
from contextlib import contextmanager
import colorama
from colorama import Fore, Style

DB_FILE = "bpdb.sqlite3"

colorama.init(autoreset=True)

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return color + message + Style.RESET_ALL

def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    formatter = ColorFormatter("%(asctime)s %(levelname)s: %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    file_handler = logging.FileHandler("bpdb.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    file_handler.setLevel(level)

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

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
                name TEXT NOT NULL,
                start_time TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)
    logging.info("Database initialized.")

def add_session(name):
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO sessions (name, start_time) VALUES (?, ?)",
            (name, datetime.utcnow().isoformat())
        )
    logging.info(f"Added session '{name}'")

def load_plugin(name):
    """
    Dynamisch ein Plugin-Modul laden (z.B. bpdb.plugins.scapy_plugin)
    Erwartet eine Klasse DevicePlugin im Modul.
    """
    try:
        module = importlib.import_module(f"bpdb.plugins.{name}_plugin")
        # Suche nach DevicePlugin Klasse im Modul
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr.__name__ == "DevicePlugin":
                plugin_class = attr
                break
        if plugin_class is None:
            raise ImportError(f"DevicePlugin-Klasse nicht in bpdb.plugins.{name}_plugin gefunden")
        logging.info(f"Plugin '{name}' geladen: Klasse DevicePlugin gefunden")
        return plugin_class
    except Exception as e:
        logging.error(f"Fehler beim Laden des Plugins '{name}': {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="bpdb - Offensive Security DB CLI")
    parser.add_argument("--init-db", action="store_true", help="Datenbank initialisieren")
    parser.add_argument("--add-session", type=str, metavar="NAME", help="Neue Session anlegen")
    parser.add_argument("--plugin", choices=["scapy", "airopy"], help="Device Plugin laden")
    parser.add_argument("-v", "--verbose", action="store_true", help="Ausführliche Logs")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    if args.init_db:
        init_db()
        print(Fore.GREEN + "Datenbank wurde initialisiert." + Style.RESET_ALL)
        sys.exit(0)

    if args.add_session:
        add_session(args.add_session)
        print(Fore.GREEN + f"Session '{args.add_session}' wurde hinzugefügt." + Style.RESET_ALL)
        sys.exit(0)

    if args.plugin:
        init_db()  # sicherstellen, dass DB da ist
        PluginClass = load_plugin(args.plugin)
        plugin_instance = PluginClass(interface="wlan0")  # Beispiel-Interface

        try:
            logging.info("Starte Capture...")
            plugin_instance.start_capture()
        except KeyboardInterrupt:
            logging.info("Capture durch Benutzer unterbrochen")
        except Exception as e:
            logging.error(f"Fehler im Capture: {e}")
        finally:
            try:
                plugin_instance.stop_capture()
                logging.info("Capture beendet.")
            except Exception as e:
                logging.error(f"Fehler beim Stoppen des Captures: {e}")
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
