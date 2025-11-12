import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/database.db"))

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("🔍 Verificando estructura actual de la tabla 'solicitudes'...")

# 1. Verificar si ya existe la columna id
cur.execute("PRAGMA table_info(solicitudes)")
cols = [c[1] for c in cur.fetchall()]

if "id" in cols:
    print("✅ La tabla ya tiene columna 'id'. No es necesario modificar.")
else:
    print("⚙️ Creando tabla temporal sin restricción UNIQUE en numero_sic...")

    # 2. Crear tabla nueva sin la restricción
    cur.execute("""
    CREATE TABLE IF NOT EXISTS solicitudes_nueva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_sic TEXT,
        fecha_solicitud TEXT,
        OC TEXT,
        Planta TEXT,
        Material TEXT,
        Cantidad REAL,
        Unidad TEXT,
        Estado TEXT,
        solicitante_id INTEGER,
        fecha_necesidad TEXT
    );
    """)

    # 3. Copiar datos antiguos si existen
    cur.execute("""
    INSERT INTO solicitudes_nueva (
        numero_sic, fecha_solicitud, OC, Planta, Material, Cantidad, Unidad, Estado
    )
    SELECT numero_sic, fecha_solicitud, OC, Planta, Material, Cantidad, Unidad, Estado
    FROM solicitudes;
    """)

    # 4. Renombrar tablas
    cur.execute("ALTER TABLE solicitudes RENAME TO solicitudes_old;")
    cur.execute("ALTER TABLE solicitudes_nueva RENAME TO solicitudes;")
    print("✅ Tabla actualizada correctamente. (Se agregó 'id' y se eliminó UNIQUE en numero_sic)")

conn.commit()
conn.close()
print("🚀 Proceso terminado sin errores.")
