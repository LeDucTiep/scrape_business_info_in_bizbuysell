import random
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
cmd2 = '''insert into results ([Listing type]     ,
    Name                    ,
    Location                ,
    Industry               ,
    [Asking Price]          ,
    Revenue                ,
    [Cash flow]             ,
    EBITDA                 ,
    [Established date]) values (\''''

with sqlite3.connect("database_copy.db") as conn:
    cursor = conn.execute(cmd)
    conn.commit()


for i in cursor:
    l = ['Established business', 'Asset sales', 'Startups']
    
    cmd3 = l[random.randint(0,2)]+"', '"+i[1]+"', '"+ i[2]+"', '"+i[3]+"', '"+i[4]+"', '"+i[5]+"', '"+ i[6]+"', '"+i[7]+"', '"+i[8]+"')"
    try:
        with sqlite3.connect("database.db") as conn:
            conn.execute(cmd2+cmd3)
            conn.commit()
    except:pass
    cmd3 = ""