import sqlite3

cmd = "update data set status = 0"
with sqlite3.connect("database.db") as conn:
    conn.execute(cmd)
    conn.commit()
