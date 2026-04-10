from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class ProfilePayload(BaseModel):
    """Request body for creating or updating a profile."""

    description: str = Field(default="Custom profile", min_length=1, max_length=140)
    left_bound: float = Field(default=0.35, ge=0.05, le=0.90)
    right_bound: float = Field(default=0.65, ge=0.10, le=0.95)
    detection_confidence: float = Field(default=0.7, ge=0.1, le=1.0)
    presence_confidence: float = Field(default=0.7, ge=0.1, le=1.0)
    tracking_confidence: float = Field(default=0.6, ge=0.1, le=1.0)
    cooldown_ms: int = Field(default=220, ge=80, le=1200)

    @model_validator(mode="after")
    def _bounds_order(self) -> ProfilePayload:
        if self.left_bound >= self.right_bound:
            raise ValueError(
                f"left_bound ({self.left_bound}) must be strictly less than "
                f"right_bound ({self.right_bound})."
            )
        return self


class ProfileItem(BaseModel):
    """Single profile as returned by the API."""

    name: str
    description: str
    left_bound: float
    right_bound: float
    detection_confidence: float
    presence_confidence: float
    tracking_confidence: float
    cooldown_ms: int


class ProfileListResponse(BaseModel):
    """Response for GET /v1/profiles."""

    active: str
    items: list[ProfileItem]


class ProfileActionResponse(BaseModel):
    """Response for PUT/POST on profile endpoints."""

    status: str
    profile: dict[str, Any]


class TelemetryResponse(BaseModel):
    """Response for GET /v1/telemetry."""

    latest: dict[str, Any] | None = None
    history: list[dict[str, Any]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Response for GET /v1/health."""

    status: str
    service: str
