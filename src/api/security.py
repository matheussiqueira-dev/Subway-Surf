from __future__ import annotations

import secrets
from collections.abc import Callable
from typing import Annotated

from fastapi import Header, HTTPException, status


def api_key_guard(expected_api_key: str) -> Callable[..., None]:
    """FastAPI dependency factory that validates the ``x-api-key`` header.

    When *expected_api_key* is an empty string authentication is disabled,
    which is the default development mode.  In production set ``API_KEY``
    to a randomly generated value (e.g. ``python -c "import secrets; print(secrets.token_urlsafe(32))"``)

    Uses :func:`secrets.compare_digest` to prevent timing-based side-channel
    attacks that would allow an attacker to enumerate valid key prefixes.
    """

    def guard(x_api_key: Annotated[str | None, Header()] = None) -> None:
        if not expected_api_key:
            return
        provided = x_api_key or ""
        if not secrets.compare_digest(provided, expected_api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key.",
                headers={"WWW-Authenticate": "ApiKey"},
            )

    return guard
