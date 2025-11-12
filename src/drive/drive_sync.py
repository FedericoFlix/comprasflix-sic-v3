from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def conectar_drive():
    """Autentica y devuelve una instancia de GoogleDrive con token persistente"""
    gauth = GoogleAuth()

    # Archivo local donde se guarda el token
    cred_file = "credentials.json"

    # Si ya existe el token, usarlo
    if os.path.exists(cred_file):
        gauth.LoadCredentialsFile(cred_file)
        if gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
    else:
        # Autenticación inicial (solo la primera vez)
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(cred_file)

    return GoogleDrive(gauth)

def listar_archivos():
    """Lista los archivos del Drive raíz"""
    drive = conectar_drive()
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    print("\nArchivos en tu Google Drive:\n")
    for file in file_list:
        print(f"{file['title']} ({file['id']})")

if __name__ == "__main__":
    print("Conectando con Google Drive...")
    listar_archivos()
