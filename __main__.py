#!/usr/bin/env python3
# blcrpython3/__main__.py

import sys
import importlib
import traceback

MODULES = [
    "bpython.args",
    "bpython.autocomplete",
    "bpython.lazyre",
    "bpython.config",
    "bpython.translations",
    "bpython.repl",  # wichtig für UI
    "bpython.curtsiesfrontend.repl",  # optional
    "bpython.inspection",
    "bpython.formatter"
]

OPTIONAL_DEPENDENCIES = [
    "scapy.all",
    "subprocess",
    "sqlite3",
    "tkinter",
    "matplotlib",
    "espeak",  # optional für Sprachausgabe (Linux)
    "cmd2"
]

def try_import(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"[WARN] Konnte Modul nicht laden: {module_name} -> {e}")
        return None

def main():
    print("🚀 Starte BLCRPython3 Interactive Terminal")
    print("🔍 Lade interne Module:")
    
    loaded_modules = {}
    for mod in MODULES:
        print(f"  └─ {mod}...", end="")
        try:
            loaded_modules[mod] = importlib.import_module(mod)
            print(" OK")
        except Exception as e:
            print(" FEHLER")
            traceback.print_exc()

    print("\n🧪 Prüfe externe Abhängigkeiten:")
    for dep in OPTIONAL_DEPENDENCIES:
        print(f"  └─ {dep}...", end="")
        try:
            importlib.import_module(dep)
            print(" OK")
        except ImportError:
            print(" FEHLT")

    # Optional: SQLite-Init
    print("\n📦 SQLite-Test:")
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO test (name) VALUES ('Jan')")
        conn.commit()
        result = cursor.execute("SELECT * FROM test").fetchall()
        print("  → SQLite OK:", result)
        conn.close()
    except Exception as e:
        print("  → SQLite Fehler:", e)

    # Optional: Start REPL
    print("\n🧠 Starte bpython REPL...")
    try:
        from bpython import embed
        embed(locals_=locals(), banner="BLCRPython3 — Red & Blue Terminal")
    except Exception as e:
        print("[FEHLER] Beim Start des Interpreters:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[EXIT] Benutzerabbruch.")
    except Exception as e:
        print("\n[CRITICAL] Unbehandelter Fehler:")
        traceback.print_exc()
