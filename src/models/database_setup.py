import sqlite3
from datetime import datetime

DB_PATH = "src/database/database.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    # Tabla de solicitudes (SIC)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_sic TEXT NOT NULL UNIQUE,
            fecha_solicitud TEXT NOT NULL,
            oc TEXT,
            planta TEXT,
            material TEXT,
            cantidad REAL,
            unidad TEXT,
            estado TEXT DEFAULT 'Solicitado',
            solicitante_id INTEGER,
            fecha_necesidad TEXT,
            FOREIGN KEY (solicitante_id) REFERENCES usuarios (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Tablas creadas correctamente.")


if __name__ == "__main__":
    create_tables()
