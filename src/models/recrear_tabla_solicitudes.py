import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/database.db"))

print(f"Usando base de datos: {DB_PATH}")

if not os.path.exists(DB_PATH):
    print("❌ No se encontró la base de datos.")
    raise SystemExit()

# Crear backup antes de modificar
backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "backups"))
os.makedirs(backup_dir, exist_ok=True)
backup_file = os.path.join(backup_dir, f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
shutil.copy2(DB_PATH, backup_file)
print(f"🔐 Backup creado en: {backup_file}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Leer columnas actuales (por si hay datos)
cur.execute("PRAGMA table_info(solicitudes)")
cols = cur.fetchall()
colnames = [c[1] for c in cols]
print("Columnas actuales:", colnames)

# 1️⃣ Renombrar tabla vieja
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
cur.execute(f"ALTER TABLE solicitudes RENAME TO solicitudes_old_{timestamp};")

# 2️⃣ Crear la tabla nueva sin UNIQUE en numero_sic
cur.execute("""
CREATE TABLE solicitudes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_sic TEXT,
    fecha_solicitud TEXT,
    oc TEXT,
    planta TEXT,
    material TEXT,
    cantidad REAL,
    unidad TEXT,
    estado TEXT DEFAULT 'Solicitado',
    solicitante_id INTEGER,
    fecha_necesidad TEXT
);
""")
print("✅ Nueva tabla creada correctamente (sin restricción UNIQUE).")

# 3️⃣ Copiar datos antiguos
old_name = f"solicitudes_old_{timestamp}"
common_cols = [c for c in colnames if c in [
    "numero_sic", "fecha_solicitud", "oc", "planta", "material",
    "cantidad", "unidad", "estado", "solicitante_id", "fecha_necesidad"
]]

if common_cols:
    cols_csv = ", ".join(common_cols)
    insert_sql = f"INSERT INTO solicitudes ({cols_csv}) SELECT {cols_csv} FROM {old_name};"
    cur.execute(insert_sql)
    conn.commit()
    print(f"📥 {cur.rowcount} registros migrados desde la tabla anterior.")
else:
    print("⚠️ No se encontraron columnas comunes para copiar datos.")

conn.commit()
conn.close()
print("🚀 Proceso completado con éxito.")
