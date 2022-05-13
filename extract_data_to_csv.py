import sqlite3

character_to_separate = "\t"

cmd = '''select [Listing type]     ,
    Name                    ,
    Location                ,
    Industry               ,
    [Asking Price]          ,
    Revenue                ,
    [Cash flow]             ,
    EBITDA                 ,
    [Established date] from results'''

with sqlite3.connect("database.db") as conn:
    cursor = conn.execute(cmd)
    conn.commit()

file = open("results.csv", "w")
file.write("Listing_type")
file.write(character_to_separate)
file.write("Name")
file.write(character_to_separate)
file.write("Location")
file.write(character_to_separate)
file.write("Industry")
file.write(character_to_separate)
file.write("Asking Price")
file.write(character_to_separate)
file.write("Revenue")
file.write(character_to_separate)
file.write("Cash flow")
file.write(character_to_separate)
file.write("EBITDA")
file.write(character_to_separate)
file.write("Established date\n")

for i in cursor:
    for j in i:
        file.write(j)
        file.write(character_to_separate)
    file.write("\n")
file.close()