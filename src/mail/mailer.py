from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import os

# -----------------------------
# Configuración general de mail
# -----------------------------
DESTINATARIOS_FIJOS = ["abastecimiento@flix-instrumentacion.com"]  # 👈 Cambiá este correo por el real

# Rutas de credenciales
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TOKEN_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../token.json"))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "../drive/credentials.json")

# Scopes requeridos (deben incluir Gmail y Drive)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.file"
]

def get_gmail_service():
    """Crea un servicio autenticado de Gmail usando las credenciales existentes."""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError("No se encontró el archivo token.json. Ejecute la autenticación primero.")
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build("gmail", "v1", credentials=creds)


def enviar_correo(numero_sic, planta, fecha_necesidad, materiales):
    """
    Envía un correo electrónico con los datos de la SIC.
    materiales: lista de tuplas [(material, cantidad, unidad), ...]
    """
    service = get_gmail_service()

    subject = f"Nueva SIC generada - SIC nº {numero_sic} - {planta}"

    cuerpo_html = f"""
    <html>
    <body>
        <h3>Se ha generado una nueva SIC</h3>
        <p><strong>Fecha de necesidad:</strong> {fecha_necesidad}</p>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr><th>Material</th><th>Cantidad</th><th>Unidad</th></tr>
            {''.join(f"<tr><td>{m}</td><td>{c}</td><td>{u}</td></tr>" for m, c, u in materiales)}
        </table>
        <p>Este mensaje fue generado automáticamente por el sistema SIC.</p>
    </body>
    </html>
    """

    message = MIMEText(cuerpo_html, "html")
    message["to"] = ", ".join(DESTINATARIOS_FIJOS)
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()
        print(f"✅ Correo enviado correctamente: SIC {numero_sic}")
    except Exception as e:
        print(f"⚠️ No se pudo enviar el correo: {e}")
