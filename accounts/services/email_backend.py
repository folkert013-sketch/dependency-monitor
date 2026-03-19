import logging
import os

import msal
import requests

logger = logging.getLogger(__name__)

_token_cache = msal.SerializableTokenCache()


def _get_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
        token_cache=_token_cache,
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "Unknown error"))
        raise RuntimeError(f"Token acquisition failed: {error}")
    return result["access_token"]


def send_email(
    to: str | list[str],
    subject: str,
    plain_body: str,
    html_body: str,
    from_address: str | None = None,
    display_name: str | None = None,
    attachments: list[dict] | None = None,
):
    tenant_id = os.environ.get("MS_GRAPH_TENANT_ID", "")
    client_id = os.environ.get("MS_GRAPH_CLIENT_ID", "")
    client_secret = os.environ.get("MS_GRAPH_CLIENT_SECRET", "")
    user_id = from_address or os.environ.get("MS_GRAPH_USER_ID", "")

    if not all([tenant_id, client_id, client_secret, user_id]):
        raise RuntimeError("MS_GRAPH_TENANT_ID, MS_GRAPH_CLIENT_ID, MS_GRAPH_CLIENT_SECRET and MS_GRAPH_USER_ID must be set.")

    token = _get_token(tenant_id, client_id, client_secret)
    _send_via_graph(token, user_id, to, subject, plain_body, html_body, display_name, attachments)


def send_email_from_settings(es, to: str | list[str], subject: str, plain_body: str, html_body: str):
    tenant_id = es.graph_tenant_id or os.environ.get("MS_GRAPH_TENANT_ID", "")
    client_id = es.graph_client_id or os.environ.get("MS_GRAPH_CLIENT_ID", "")
    client_secret = es.graph_client_secret or os.environ.get("MS_GRAPH_CLIENT_SECRET", "")
    user_id = es.smtp_user

    if not all([tenant_id, client_id, client_secret, user_id]):
        raise RuntimeError("Graph API credentials incompleet.")

    token = _get_token(tenant_id, client_id, client_secret)
    _send_via_graph(token, user_id, to, subject, plain_body, html_body, es.display_name or None)


def test_connection_from_settings(es):
    tenant_id = es.graph_tenant_id or os.environ.get("MS_GRAPH_TENANT_ID", "")
    client_id = es.graph_client_id or os.environ.get("MS_GRAPH_CLIENT_ID", "")
    client_secret = es.graph_client_secret or os.environ.get("MS_GRAPH_CLIENT_SECRET", "")
    user_id = es.smtp_user

    if not all([tenant_id, client_id, client_secret, user_id]):
        raise RuntimeError("Vul eerst alle Graph API velden en het e-mailadres in.")

    token = _get_token(tenant_id, client_id, client_secret)

    # Verify mailbox access
    resp = requests.get(
        f"https://graph.microsoft.com/v1.0/users/{user_id}/mailFolders/inbox",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Mailbox toegang mislukt ({resp.status_code}): {resp.text[:200]}")


def _send_via_graph(
    token: str,
    user_id: str,
    to: str | list[str],
    subject: str,
    plain_body: str,
    html_body: str,
    display_name: str | None = None,
    attachments: list[dict] | None = None,
):
    recipients = [to] if isinstance(to, str) else to
    to_recipients = [
        {"emailAddress": {"address": addr}} for addr in recipients
    ]

    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": html_body,
            },
            "toRecipients": to_recipients,
        },
        "saveToSentItems": True,
    }

    if display_name:
        payload["message"]["from"] = {
            "emailAddress": {"address": user_id, "name": display_name}
        }

    if attachments:
        payload["message"]["attachments"] = attachments

    resp = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{user_id}/sendMail",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if resp.status_code not in (200, 202):
        raise RuntimeError(f"Graph API sendMail failed ({resp.status_code}): {resp.text[:300]}")
