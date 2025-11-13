from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Ruta al credentials.json que ya usás para Google Drive
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"

# Alcances: Gmail y Drive (pueden coexistir)
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.send"
]

flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
creds = flow.run_local_server(port=0)
with open(TOKEN_PATH, "w") as token:
    token.write(creds.to_json())

print(f"✅ Token generado correctamente en: {os.path.abspath(TOKEN_PATH)}")
