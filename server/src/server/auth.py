import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthSettings:
    """Keycloak configuration for validating incoming agent tokens."""

    realm_url: str
    base_url: str

    @classmethod
    def from_env(cls) -> "AuthSettings":
        """Read settings from the environment.

        Raises:
            RuntimeError: if a required variable is not set.
        """
        realm_url = os.getenv("KEYCLOAK_REALM_URL")
        if realm_url is None:
            raise RuntimeError("KEYCLOAK_REALM_URL is not set")
        base_url = os.getenv("MCP_BASE_URL")
        if base_url is None:
            raise RuntimeError("MCP_BASE_URL is not set")
        return cls(realm_url=realm_url, base_url=base_url)
