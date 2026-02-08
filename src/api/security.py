from __future__ import annotations

from typing import Annotated, Callable

from fastapi import Header, HTTPException, status


def api_key_guard(expected_api_key: str) -> Callable[..., None]:
    def guard(x_api_key: Annotated[str | None, Header()] = None) -> None:
        if not expected_api_key:
            return
        if x_api_key != expected_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key.",
            )

    return guard

