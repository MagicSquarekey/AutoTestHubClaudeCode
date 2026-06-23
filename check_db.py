# -*- coding: utf-8 -*-
"""查询数据库中的测试数据"""
import sqlite3
import json
import os

db_path = os.path.join(os.path.dirname(__file__), "backend", "data", "autotest.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("=== test_element (全部) ===")
c.execute("SELECT id, elem_name, page_name, module, locators FROM test_element")
for row in c.fetchall():
    print(f"  #{row[0]} | {row[1]} | page={row[2]} | module={row[3]}")
    if row[4]:
        try:
            locators = json.loads(row[4])
            for loc in locators[:2]:
                plat = loc.get("platform", "?")
                val = loc.get("locator_value", "")[:80]
                print(f"    locator: {plat} -> {val}")
        except Exception as e:
            print(f"    locator parse error: {e}")

print()
print("=== test_case (全部) ===")
c.execute(
    "SELECT id, case_name, case_type, priority, status, module_path, tags "
    "FROM test_case"
)
for row in c.fetchall():
    print(
        f"  #{row[0]} | {row[1]} | type={row[2]} | pri={row[3]} "
        f"| status={row[4]} | module={row[5]} | tags={row[6]}"
    )

print()
print("=== test_suite (全部) ===")
c.execute("SELECT id, suite_name, suite_type, parent_id FROM test_suite")
for row in c.fetchall():
    print(f"  #{row[0]} | {row[1]} | type={row[2]} | parent={row[3]}")

conn.close()
