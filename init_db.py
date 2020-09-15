import sqlite3

connection = sqlite3.connect('database.db')
with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()
cur.execute("INSERT INTO verses(title, content) VALUES (?, ?)",
            ('First Verse', 'Content for the first verse')
            )

cur.execute("INSERT INTO verses(title, content) VALUES (?, ?)",
            ('Second Verse', 'Content for the second verse')
            )


cur.execute("INSERT INTO guests(guestname, messagecontent) VALUES (?, ?)",
            ('First message', 'Content for the first message')
            )
cur.execute("INSERT INTO guests(guestname, messagecontent) VALUES (?, ?)",
            ('First message', 'Content for the first message')
            )

connection.commit()
connection.close()
