# src/models/fix_solicitudes_unique.py
import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/database.db"))

def backup_db():
    backups_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "backups"))
    os.makedirs(backups_dir, exist_ok=True)
    dest = os.path.join(backups_dir, f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy2(DB_PATH, dest)
    print(f"🔐 Backup creado en: {dest}")
    return dest

def inspect_table(conn, table_name="solicitudes"):
    cur = conn.cursor()
    print("\n🔎 PRAGMA table_info:")
    cur.execute(f"PRAGMA table_info({table_name})")
    cols = cur.fetchall()
    for c in cols:
        print(c)
    print("\n🔎 PRAGMA index_list:")
    cur.execute(f"PRAGMA index_list({table_name})")
    idxs = cur.fetchall()
    for i in idxs:
        print(i)
    return cols, idxs

def drop_unique_index_if_exists(conn, table_name="solicitudes"):
    cur = conn.cursor()
    cur.execute(f"PRAGMA index_list({table_name})")
    idxs = cur.fetchall()
    dropped = False
    for idx in idxs:
        idx_name = idx[1]  # index name
        is_unique = idx[2]  # 1 if unique
        if is_unique:
            # inspect index columns
            cur.execute(f"PRAGMA index_info({idx_name})")
            info = cur.fetchall()
            cols = [r[2] for r in info]
            if "numero_sic" in cols:
                print(f"⚠️ Se encontró índice único '{idx_name}' sobre columnas {cols}. Se intentará eliminarlo.")
                conn.execute(f"DROP INDEX IF EXISTS {idx_name}")
                conn.commit()
                print(f"✅ Índice '{idx_name}' eliminado.")
                dropped = True
    return dropped

def recreate_table_without_unique(conn, table_name="solicitudes"):
    cur = conn.cursor()
    # read current columns
    cur.execute(f"PRAGMA table_info({table_name})")
    cols = cur.fetchall()
    col_names = [c[1] for c in cols]
    print(f"\nColumnas actuales: {col_names}")

    # build new table name
    new_table = f"{table_name}_new"

    # define new schema: ensure id INTEGER PRIMARY KEY AUTOINCREMENT exists, and numero_sic TEXT (no UNIQUE)
    # We'll keep other columns with TEXT type for safety if original types missing
    # Try to preserve types from PRAGMA if available
    col_defs = []
    has_id = False
    for c in cols:
        name = c[1]
        typ = c[2] if c[2] else "TEXT"
        if name.lower() == "id":
            has_id = True
            col_defs.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            # ensure numero_sic is TEXT (no UNIQUE)
            if name.lower() == "numero_sic":
                col_defs.append("numero_sic TEXT")
            else:
                col_defs.append(f"{name} {typ}")
    if not has_id:
        # prepend id
        col_defs.insert(0, "id INTEGER PRIMARY KEY AUTOINCREMENT")

    create_sql = f"CREATE TABLE IF NOT EXISTS {new_table} ({', '.join(col_defs)});"
    print(f"\n⚙️ Creando nueva tabla: {new_table}")
    cur.execute(create_sql)

    # copy data (map columns that exist in both)
    # columns to copy: intersection of existing column names (excluding id in new if it didn't exist)
    cur.execute(f"PRAGMA table_info({new_table})")
    new_cols = [c[1] for c in cur.fetchall()]
    # prepare list of columns to copy from old -> new (only those that exist in both)
    common_cols = [c for c in col_names if c in new_cols and c.lower() != "id"]
    if not common_cols:
        print("❌ No se encontraron columnas comunes para copiar datos. Abortando.")
        return False

    cols_csv = ", ".join(common_cols)
    insert_sql = f"INSERT INTO {new_table} ({cols_csv}) SELECT {cols_csv} FROM {table_name};"
    print(f"⚙️ Copiando datos: {insert_sql}")
    cur.execute(insert_sql)
    conn.commit()

    # rename tables
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    old_name = f"{table_name}_old_{timestamp}"
    print(f"⚙️ Renombrando tabla original a {old_name}")
    cur.execute(f"ALTER TABLE {table_name} RENAME TO {old_name};")
    cur.execute(f"ALTER TABLE {new_table} RENAME TO {table_name};")
    conn.commit()
    print("✅ Tabla recreada y datos migrados correctamente.")
    return True

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró la base de datos en {DB_PATH}")
        return
    print(f"Usando DB: {DB_PATH}")
    backup_db()
    conn = sqlite3.connect(DB_PATH)

    try:
        cols, idxs = inspect_table(conn, "solicitudes")
        # step 1: try to drop unique index on numero_sic
        dropped = drop_unique_index_if_exists(conn, "solicitudes")
        if dropped:
            print("✅ Se eliminó un índice único que causaba el problema. Verifica con tu app.")
            conn.close()
            return

        # step 2: if no unique index found, attempt to recreate table without unique
        print("ℹ️ No se encontró índice único sobre 'numero_sic' o no pudo eliminarse. Intentando recrear la tabla sin UNIQUE...")
        ok = recreate_table_without_unique(conn, "solicitudes")
        if ok:
            print("✅ Operación finalizada: la tabla 'solicitudes' ahora permite numero_sic duplicados.")
        else:
            print("❌ No se pudo recrear la tabla automáticamente. Revisá manualmente la DB.")
    except Exception as e:
        print("❌ Ocurrió un error:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
