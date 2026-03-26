import os

import bleach
from crewai.tools import BaseTool

# Allowed HTML tags/attributes for email content from LLM output
_ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "br", "hr",
    "strong", "b", "em", "i", "u", "s", "sub", "sup",
    "ul", "ol", "li", "dl", "dt", "dd",
    "table", "thead", "tbody", "tr", "th", "td",
    "a", "img", "span", "div", "blockquote", "pre", "code",
]
_ALLOWED_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "alt", "width", "height"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
    "*": ["style"],
}
_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


class EmailSenderTool(BaseTool):
    name: str = "Email Sender"
    description: str = (
        "Sends an HTML email report. Input should be a string in the format: "
        "'SUBJECT: <subject line>\\n\\nBODY:\\n<html content>'. "
        "Uses Microsoft Graph API to send email."
    )

    def _run(self, email_content: str) -> str:
        if "SUBJECT:" not in email_content or "BODY:" not in email_content:
            return "ERROR: Input must contain 'SUBJECT: ...' and 'BODY:\\n...' sections."

        parts = email_content.split("BODY:", 1)
        subject_line = parts[0].replace("SUBJECT:", "").strip()
        html_body = parts[1].strip()

        # Sanitize LLM-generated HTML to prevent script injection
        html_body = bleach.clean(
            html_body,
            tags=_ALLOWED_TAGS,
            attributes=_ALLOWED_ATTRS,
            protocols=_ALLOWED_PROTOCOLS,
            strip=True,
        )

        email_to = os.environ.get("EMAIL_TO", os.environ.get("MS_GRAPH_USER_ID", ""))

        if not email_to:
            return "ERROR: EMAIL_TO or MS_GRAPH_USER_ID environment variable must be set."

        plain_text = html_body.replace("<br>", "\n").replace("</p>", "\n").replace("</div>", "\n")

        try:
            from accounts.services.email_backend import send_email
            send_email(email_to, subject_line, plain_text, html_body)
            return f"Email sent successfully to {email_to} with subject: {subject_line}"
        except Exception as e:
            return f"ERROR sending email: {e}"
