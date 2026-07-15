import os
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)

class EmailService:
    """
    Handles executive report distribution via SMTP.
    Supports local logging simulation if SMTP credentials are not set.
    """
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 smtp_user: str = None, smtp_password: str = None):
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        
        # Outbox log path for offline simulation
        self.simulated_outbox_path = "d:/project/data/simulated_email_outbox.log"

    def is_smtp_configured(self) -> bool:
        """Verifies if SMTP coordinates are set."""
        return bool(self.smtp_server and self.smtp_user and self.smtp_password)

    def send_report_email(self, recipient_email: str, subject: str, body_text: str, attachment_path: str = None) -> dict:
        """
        Sends email with PDF attachment.
        If SMTP details are missing, performs a high-fidelity local outbox log simulation.
        """
        if not self.is_smtp_configured():
            logger.info("SMTP not configured. Simulating outbox delivery.")
            return self._simulate_email(recipient_email, subject, body_text, attachment_path)

        try:
            # 1. Setup email structure
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Body text (HTML format can also be set up, using plain text as base)
            msg.attach(MIMEText(body_text, 'plain'))
            
            # Attachment
            if attachment_path and os.path.exists(attachment_path):
                filename = os.path.basename(attachment_path)
                with open(attachment_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    msg.attach(part)
                    
            # 2. Open connection and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, recipient_email, msg.as_string())
            server.quit()
            
            logger.info(f"Successfully sent email to {recipient_email}")
            return {
                "status": "SENT",
                "mode": "SMTP",
                "timestamp": datetime.now().isoformat(),
                "recipient": recipient_email
            }
            
        except Exception as e:
            logger.error(f"Failed to send actual email via SMTP: {e}")
            logger.info("Falling back to local email simulation.")
            return self._simulate_email(recipient_email, f"[SMTP FAIL FALLBACK] {subject}", body_text, attachment_path, error_msg=str(e))

    def _simulate_email(self, recipient_email: str, subject: str, body_text: str, attachment_path: str = None, error_msg: str = None) -> dict:
        """Logs simulated email transactions to a local file for offline validation."""
        timestamp = datetime.now().isoformat()
        log_entry = f"""
========================================
[SIMULATED EMAIL TRANSACTION]
Timestamp: {timestamp}
Status: DELIVERED (SIMULATED)
To: {recipient_email}
Subject: {subject}
Attachment: {attachment_path or "None"}
{f"SMTP Error Logged: {error_msg}" if error_msg else "SMTP: Not Configured (Local Mode)"}
----------------------------------------
Message Body:
{body_text}
========================================
"""
        # Ensure data folder exists
        os.makedirs(os.path.dirname(self.simulated_outbox_path), exist_ok=True)
        
        with open(self.simulated_outbox_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        logger.info(f"Simulated email written to {self.simulated_outbox_path}")
        return {
            "status": "SIMULATED",
            "mode": "LOCAL_LOGGER",
            "timestamp": timestamp,
            "recipient": recipient_email,
            "outbox_log": self.simulated_outbox_path
        }
