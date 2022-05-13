import sqlite3

with sqlite3.connect("database.db") as conn:
    cmd = "select * from data"
    cor = conn.execute(cmd)
    conn.commit()

dem = 0
for i in cor:
    dem+=1
print("Links to second pages: ", dem)

cmd = "select * from results"
with sqlite3.connect("database.db") as conn:
    cor = conn.execute(cmd)
    conn.commit()

dem = 0
for i in cor:
    dem+=1

print("Data records: ", dem)
input()