"""Transparent Fernet encryption for CharField values.

Uses a dedicated ENCRYPTION_KEY (falls back to SECRET_KEY for backwards compat).
Backwards compatible: unencrypted plaintext values are returned as-is.
"""

import base64
import hashlib

from django.conf import settings
from django.db import models


def _get_fernet():
    from cryptography.fernet import Fernet

    # Use dedicated ENCRYPTION_KEY if available, fall back to SECRET_KEY
    source_key = getattr(settings, "ENCRYPTION_KEY", "") or settings.SECRET_KEY
    key = hashlib.sha256(source_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


class EncryptedCharField(models.CharField):
    """CharField that transparently encrypts values at rest using Fernet."""

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return _get_fernet().decrypt(value.encode()).decode()
        except Exception:
            # Backwards compatible: return plaintext if decryption fails
            return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        return _get_fernet().encrypt(value.encode()).decode()

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, "accounts.fields.EncryptedCharField", args, kwargs
