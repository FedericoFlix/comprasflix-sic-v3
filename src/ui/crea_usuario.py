import sqlite3
conn = sqlite3.connect("src/database/database.db")
conn.execute("INSERT INTO usuarios (nombre) VALUES ('Federico')")
conn.commit()
conn.close()
