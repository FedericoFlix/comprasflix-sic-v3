from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64

def enviar_mail_gmail_api(numero_sic, fecha_necesidad, oc, planta, items, destinatario="compras@empresa.com"):
    """
    Envía un mail HTML con los datos de la SIC usando Gmail API.
    Requiere tener token.json con scope: gmail.send
    """
    try:
        creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.send"])
        service = build("gmail", "v1", credentials=creds)

        # --- Asunto y cuerpo HTML ---
        asunto = f"Se generó una nueva SIC número: {numero_sic}"
        cuerpo_html = f"""
        <html>
        <body>
            <p>
            Nueva Solicitud Interna de Compra Nº <b>{numero_sic}</b><br>
            Fecha esperada de recepción: <b>{fecha_necesidad}</b><br>
            Orden de compra: <b>{oc}</b><br>
            Planta: <b>{planta}</b>
            </p>
            <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse;">
                <tr style="background-color:#f2f2f2;">
                    <th>Descripción</th>
                    <th>Cantidad</th>
                    <th>Unidad</th>
                </tr>
        """

        for desc, cant, unidad in items:
            cuerpo_html += f"""
                <tr>
                    <td>{desc}</td>
                    <td align="center">{cant}</td>
                    <td align="center">{unidad}</td>
                </tr>
            """

        cuerpo_html += """
            </table>
            <p>Este correo fue generado automáticamente por el sistema SIC.</p>
        </body>
        </html>
        """

        # --- Crear mensaje ---
        message = MIMEText(cuerpo_html, "html")
        message["to"] = destinatario
        message["subject"] = asunto

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {"raw": raw_message}

        # --- Enviar ---
        service.users().messages().send(userId="me", body=message_body).execute()
        print("✅ Correo enviado correctamente vía Gmail API.")

    except Exception as e:
        print(f"⚠️ Error al enviar correo vía Gmail API: {e}")
