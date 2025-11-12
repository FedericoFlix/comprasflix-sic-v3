import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../database/sic.db")

def conectar():
    """Devuelve una conexión a la base de datos"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def crear_tablas():
    """Crea las tablas si no existen"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            proveedor TEXT NOT NULL,
            detalle TEXT,
            monto REAL NOT NULL,
            estado TEXT DEFAULT 'pendiente'
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_tablas()
    print("✅ Base de datos inicializada correctamente.")
