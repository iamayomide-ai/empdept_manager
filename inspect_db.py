import sqlite3
c = sqlite3.connect('empdept.db')
for name, sql in c.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall():
    print('-----', name)
    print(sql)
    n = c.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
    print('rows:', n)
    print('foreign keys:', c.execute(f'PRAGMA foreign_key_list("{name}")').fetchall())
    print('indexes:', c.execute(f'PRAGMA index_list("{name}")').fetchall())
