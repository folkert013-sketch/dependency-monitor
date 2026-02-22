import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from crewai.tools import BaseTool


class EmailSenderTool(BaseTool):
    name: str = "Email Sender"
    description: str = (
        "Sends an HTML email report. Input should be a string in the format: "
        "'SUBJECT: <subject line>\\n\\nBODY:\\n<html content>'. "
        "Uses Gmail SMTP with app password from environment variables."
    )

    def _run(self, email_content: str) -> str:
        # Parse subject and body
        if "SUBJECT:" not in email_content or "BODY:" not in email_content:
            return "ERROR: Input must contain 'SUBJECT: ...' and 'BODY:\\n...' sections."

        parts = email_content.split("BODY:", 1)
        subject_line = parts[0].replace("SUBJECT:", "").strip()
        html_body = parts[1].strip()

        # Get SMTP config from environment
        smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "465"))
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_password = os.environ.get("SMTP_PASSWORD", "")
        email_to = os.environ.get("EMAIL_TO", smtp_user)

        if not smtp_user or not smtp_password:
            return "ERROR: SMTP_USER and SMTP_PASSWORD environment variables must be set."

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject_line
        msg["From"] = smtp_user
        msg["To"] = email_to

        # Create plain text fallback
        plain_text = html_body.replace("<br>", "\n").replace("</p>", "\n").replace("</div>", "\n")

        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [email_to], msg.as_string())
            return f"Email sent successfully to {email_to} with subject: {subject_line}"
        except Exception as e:
            return f"ERROR sending email: {e}"
