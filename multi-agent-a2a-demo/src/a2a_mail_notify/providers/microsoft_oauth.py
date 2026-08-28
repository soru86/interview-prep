from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import msal

from a2a_mail_notify.logging import get_logger

log = get_logger(__name__)

# MSAL device-code flow rejects reserved scopes (openid, profile, offline_access).
# offline_access is requested automatically so the refresh token can be cached.
IMAP_SCOPES = [
    "https://outlook.office.com/IMAP.AccessAsUser.All",
]


def xoauth2_payload(username: str, access_token: str) -> bytes:
    return f"user={username}\x01auth=Bearer {access_token}\x01\x01".encode()


class MicrosoftImapAuth:
    """MSAL public-client helper for Outlook.com / Microsoft 365 IMAP (XOAUTH2)."""

    def __init__(
        self,
        client_id: str,
        tenant: str,
        username: str,
        cache_path: Path,
    ) -> None:
        self.client_id = client_id
        self.tenant = tenant or "consumers"
        self.username = username
        self.cache_path = cache_path
        self._cache = msal.SerializableTokenCache()
        if cache_path.exists():
            self._cache.deserialize(cache_path.read_text(encoding="utf-8"))
        self._app = msal.PublicClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant}",
            token_cache=self._cache,
        )

    def _persist_cache(self) -> None:
        if not self._cache.has_state_changed:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(self._cache.serialize(), encoding="utf-8")
        log.info("msal_token_cache_saved", path=str(self.cache_path))

    def acquire_silent(self) -> str:
        if not self.client_id:
            raise RuntimeError(
                "mailbox.oauth_client_id is empty. In entra.microsoft.com create an app "
                "(Personal accounts only), enable Allow public client flows, and paste the Application (client) ID."
            )
        accounts = self._app.get_accounts(username=self.username) or self._app.get_accounts()
        result = None
        if accounts:
            result = self._app.acquire_token_silent(IMAP_SCOPES, account=accounts[0])
        self._persist_cache()
        if not result or "access_token" not in result:
            raise RuntimeError(
                "No Outlook OAuth token on disk. Run: a2a-mail-notify login"
            )
        log.info("msal_token_silent", username=self.username)
        return str(result["access_token"])

    def acquire_device_code(self, printer: Callable[[str], None] = print) -> str:
        if not self.client_id:
            raise RuntimeError(
                "mailbox.oauth_client_id is empty. In entra.microsoft.com: App registrations → "
                "New registration → Personal accounts only → Authentication → Allow public client "
                "flows = Yes. Paste the Application (client) ID into mailbox.oauth_client_id. "
                "IMAP scope is requested at login (https://outlook.office.com/IMAP.AccessAsUser.All)."
            )
        try:
            flow = self._app.initiate_device_flow(scopes=IMAP_SCOPES)
        except ValueError as exc:
            raise RuntimeError(f"Failed to start Microsoft device login: {exc}") from exc
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to start Microsoft device login: {flow}")
        printer(flow["message"])
        log.info("msal_device_flow_started")
        result = self._app.acquire_token_by_device_flow(flow)
        self._persist_cache()
        if not result or "access_token" not in result:
            error = (result or {}).get("error_description") or (result or {}).get("error") or result
            raise RuntimeError(f"Microsoft login failed: {error}")
        log.info("msal_device_flow_ok", username=self.username)
        return str(result["access_token"])
