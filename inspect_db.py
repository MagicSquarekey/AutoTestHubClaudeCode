# -*- coding: utf-8 -*-
import sqlite3, os, glob

# find db
candidates = glob.glob("**/*.db", recursive=True)
print("DB files found:", candidates)

for db_path in candidates:
    print(f"\n=== {db_path} ===")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print("Tables:", tables)
        for t in tables:
            cur.execute(f"PRAGMA table_info({t})")
            cols = [(r[1], r[2]) for r in cur.fetchall()]
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"  {t} ({cnt} rows): {cols}")
            if cnt > 0:
                cur.execute(f"SELECT * FROM {t} LIMIT 3")
                for row in cur.fetchall():
                    print(f"    sample: {row}")
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")
