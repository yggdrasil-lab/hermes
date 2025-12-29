import asyncio
import email
from aiosmtpd.controller import Controller
from app.services.email_service import EmailService
from app.core.config import settings

class HermesSMTPHandler:
    def __init__(self):
        self.email_service = EmailService()

    async def handle_DATA(self, server, session, envelope):
        try:
            # Parse the email content
            message = email.message_from_bytes(envelope.content)
            
            subject = message.get("subject", "No Subject")
            
            # Extract body
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    content_disposition = part.get("Content-Disposition")
                    if content_type == "text/plain" and "attachment" not in str(content_disposition):
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = message.get_payload(decode=True).decode()

            # Iterate over recipients (SMTP allows multiple RCPT TO)
            for recipient in envelope.rcpt_tos:
                print(f"Relaying SMTP email to {recipient} via SES (sender: {envelope.mail_from})...")
                self.email_service.send_email(
                    recipient=recipient,
                    subject=subject,
                    body=body or " ", # SES doesn't like empty body
                    sender=envelope.mail_from
                )
            
            return '250 Message accepted for delivery'
        except Exception as e:
            print(f"Error processing SMTP message: {e}")
            return '500 Internal Server Error'

def create_smtp_controller(host="0.0.0.0", port=2525):
    handler = HermesSMTPHandler()
    controller = Controller(handler, hostname=host, port=port)
    return controller
