from __future__ import annotations

from pydantic import BaseModel, Field


class ProfilePayload(BaseModel):
    description: str = Field(default="Custom profile", min_length=1, max_length=140)
    left_bound: float = Field(default=0.35, ge=0.05, le=0.90)
    right_bound: float = Field(default=0.65, ge=0.10, le=0.95)
    detection_confidence: float = Field(default=0.7, ge=0.1, le=1.0)
    presence_confidence: float = Field(default=0.7, ge=0.1, le=1.0)
    tracking_confidence: float = Field(default=0.6, ge=0.1, le=1.0)
    cooldown_ms: int = Field(default=220, ge=80, le=1200)


class TelemetryResponse(BaseModel):
    latest: dict[str, object] | None
    history: list[dict[str, object]]

