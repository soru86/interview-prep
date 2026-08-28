"""XOAUTH2 tokens for outlook.com / Office 365 mailboxes.

Microsoft disabled basic auth for IMAP, so a password in the config is not enough
for those accounts. This uses MSAL's device-code flow: the first run prints a
code to enter at microsoft.com/devicelogin, after which the refresh token is
cached on disk and renewals are silent.
"""

from __future__ import annotations

import json
from pathlib import Path

from mail_a2a.config import MailboxSettings
from mail_a2a.logging_setup import get_logger

log = get_logger(__name__)

IMAP_SCOPES = ["https://outlook.office.com/IMAP.AccessAsUser.All"]


def _load_cache(path: Path):
    import msal

    cache = msal.SerializableTokenCache()
    if path.is_file():
        try:
            cache.deserialize(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("msal_cache_unreadable", path=str(path), error=str(exc))
    return cache


def _save_cache(cache, path: Path) -> None:
    if not cache.has_state_changed:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(cache.serialize(), encoding="utf-8")
    path.chmod(0o600)
    log.info("msal_cache_saved", path=str(path))


def acquire_access_token(settings: MailboxSettings) -> str:
    """Return a bearer token for IMAP, prompting for device login if needed."""
    import msal

    if not settings.oauth_client_id:
        raise RuntimeError(
            "mailbox.auth is 'oauth2' but mailbox.oauth_client_id is empty. "
            "Register an app in Microsoft Entra ID with the delegated "
            "IMAP.AccessAsUser.All permission and put its client id in the config."
        )

    cache_path = Path(settings.oauth_token_cache)
    cache = _load_cache(cache_path)
    app = msal.PublicClientApplication(
        settings.oauth_client_id,
        authority=f"https://login.microsoftonline.com/{settings.oauth_tenant}",
        token_cache=cache,
    )

    result = None
    for account in app.get_accounts(username=settings.username or None):
        result = app.acquire_token_silent(IMAP_SCOPES, account=account)
        if result:
            log.info("msal_token_silent", username=account.get("username"))
            break

    if not result:
        flow = app.initiate_device_flow(scopes=IMAP_SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(f"Device flow failed to start: {flow.get('error_description')}")
        # Printed rather than logged: the user has to read and act on it now.
        print(f"\n[mail-a2a] {flow['message']}\n", flush=True)
        log.info("msal_device_flow_started", verification_uri=flow.get("verification_uri"))
        result = app.acquire_token_by_device_flow(flow)

    _save_cache(cache, cache_path)

    if "access_token" not in result:
        raise RuntimeError(
            f"OAuth2 token acquisition failed: {result.get('error_description') or result}"
        )
    log.info("msal_token_acquired", expires_in=result.get("expires_in"))
    return result["access_token"]
