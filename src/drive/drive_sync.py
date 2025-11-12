import os
import shutil
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# ======================
# CONFIGURACIÓN
# ======================
DB_PATH = r"C:\sic_app\src\database\database.db"

TOKEN_FILE = "mycreds.txt"
REMOTE_FILE_NAME = "database.db"
STANDARD_REMOTE_NAMES = ["database.db", "sic_database.db", "sic_database-1.db"]

# ======================
# AUTENTICACIÓN
# ======================
def conectar_drive():
    """Autentica y devuelve una instancia de GoogleDrive."""
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(TOKEN_FILE)

    if gauth.credentials is None:
        print("🔑 Autenticando por primera vez...")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print("♻️ Renovando credenciales...")
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(TOKEN_FILE)
    return GoogleDrive(gauth)

# ======================
# FUNCIONES AUXILIARES
# ======================
def obtener_archivo_drive(drive, name):
    """Devuelve el archivo remoto con el nombre especificado, o None si no existe."""
    lista = drive.ListFile({'q': f"title='{name}' and trashed=false"}).GetList()
    return lista[0] if lista else None

def listar_archivos_drive():
    """Lista todos los archivos visibles en Drive (para depuración)."""
    drive = conectar_drive()
    files = drive.ListFile({'q': "trashed=false"}).GetList()
    print("\n📂 Archivos en Drive:")
    for f in files:
        print(f" - {f['title']} (id={f['id']}, modificado={f.get('modifiedDate')})")
    return files

# ======================
# FUNCIONES DE SYNC
# ======================
def subir_base():
    """Sube o actualiza la base local al Drive."""
    drive = conectar_drive()

    if not os.path.exists(DB_PATH):
        print(f"⚠️ Base local no encontrada en {DB_PATH}")
        return

    archivo = obtener_archivo_drive(drive, REMOTE_FILE_NAME)
    if archivo:
        archivo.SetContentFile(DB_PATH)
        archivo.Upload()
        print(f"☁️ Base actualizada en Drive: {REMOTE_FILE_NAME}")
    else:
        nuevo = drive.CreateFile({'title': REMOTE_FILE_NAME})
        nuevo.SetContentFile(DB_PATH)
        nuevo.Upload()
        print(f"☁️ Base subida a Drive: {REMOTE_FILE_NAME}")

def descargar_base():
    """Descarga la versión remota sobre la base local."""
    drive = conectar_drive()
    archivo = obtener_archivo_drive(drive, REMOTE_FILE_NAME)
    if archivo:
        archivo.GetContentFile(DB_PATH)
        print("⬇️ Base descargada desde Drive correctamente.")
    else:
        print("⚠️ No se encontró la base en Drive para descargar.")

def encontrar_mejor_remoto(drive):
    """Busca entre nombres estándar y devuelve el archivo más reciente encontrado."""
    candidatos = []
    for name in STANDARD_REMOTE_NAMES:
        files = drive.ListFile({'q': f"title='{name}' and trashed=false"}).GetList()
        candidatos.extend(files)
    if not candidatos:
        todos = drive.ListFile({'q': "trashed=false"}).GetList()
        for f in todos:
            if f['title'].lower().endswith(".db"):
                candidatos.append(f)
    if not candidatos:
        return None
    candidatos.sort(key=lambda x: datetime.strptime(x['modifiedDate'], "%Y-%m-%dT%H:%M:%S.%fZ"), reverse=True)
    return candidatos[0]

def sincronizar_normalizado():
    """Sincroniza la base local y remota por fecha de modificación."""
    drive = conectar_drive()
    remoto = encontrar_mejor_remoto(drive)

    # Crear backup local
    backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backups"))
    os.makedirs(backup_dir, exist_ok=True)
    local_backup = os.path.join(backup_dir, f"local_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    if os.path.exists(DB_PATH):
        shutil.copy(DB_PATH, local_backup)
        print(f"🔐 Backup local creado: {local_backup}")

    if not remoto:
        print("⚠️ No hay base en Drive. Subiendo la local (si existe).")
        if os.path.exists(DB_PATH):
            subir_base()
        else:
            print("❌ No hay base local para subir.")
        return

    # Obtener timestamps
    remote_time = datetime.strptime(remoto['modifiedDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
    local_time = datetime.fromtimestamp(os.path.getmtime(DB_PATH)) if os.path.exists(DB_PATH) else None

    print(f"\n📄 Archivo remoto: {remoto['title']} (última modificación: {remote_time})")
    print(f"💾 Archivo local: {DB_PATH} (última modificación: {local_time})")

    if local_time is None:
        print("⬇️ No hay base local. Descargando desde Drive...")
        remoto.GetContentFile(DB_PATH)
        print("✅ Descarga completada.")
        return
    elif remote_time > local_time:
        print("🔄 La base en Drive es más reciente → descargando y sobrescribiendo local.")
        remoto.GetContentFile(DB_PATH)
        print("✅ Local actualizado desde remoto.")
    elif local_time > remote_time:
        print("🔄 La base local es más reciente → subiendo y reemplazando remoto.")
        remoto.SetContentFile(DB_PATH)
        remoto.Upload()
        print("✅ Remoto actualizado desde local.")
    else:
        print("✅ Bases sincronizadas (idénticas).")

# ======================
# TEST DIRECTO
# ======================
if __name__ == "__main__":
    sincronizar_normalizado()
