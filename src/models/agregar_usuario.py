import sqlite3

import os
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/database.db"))



def agregar_usuario(nombre):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()
    print(f"✅ Usuario '{nombre}' agregado correctamente.")

if __name__ == "__main__":
    nombre = input("Ingrese el nombre del nuevo usuario: ")
    agregar_usuario(nombre)
