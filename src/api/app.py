from __future__ import annotations

from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.schemas import (
    HealthResponse,
    ProfileActionResponse,
    ProfileListResponse,
    ProfilePayload,
    TelemetryResponse,
)
from src.api.security import api_key_guard
from src.domain.models import Profile
from src.services.profile_service import ProfileService
from src.services.telemetry_service import TelemetryService
from src.utils.config import AppConfig, load_config


def create_api_app(
    config: AppConfig | None = None,
    profile_service: ProfileService | None = None,
    telemetry_service: TelemetryService | None = None,
) -> FastAPI:
    cfg = config or load_config()
    profiles = profile_service or ProfileService(cfg.profiles_dir, cfg.active_profile_file)
    telemetry = telemetry_service or TelemetryService(cfg.telemetry_file)
    guard = api_key_guard(cfg.api_key)

    app = FastAPI(
        title="Subway Surf Motion Controller API",
        version="3.1.0",
        description=(
            "API para gestão de perfis, telemetria em tempo real e integração "
            "com dashboard do controlador por gestos.\n\n"
            "Desenvolvido por **[Matheus Siqueira](https://www.matheussiqueira.dev/)**."
        ),
        contact={
            "name": "Matheus Siqueira",
            "url": "https://www.matheussiqueira.dev/",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cfg.api_allow_origins),
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    dashboard_dir = cfg.project_root / "dashboard"
    if dashboard_dir.exists():
        app.mount(
            "/dashboard",
            StaticFiles(directory=str(dashboard_dir), html=True),
            name="dashboard",
        )

    @app.get("/", include_in_schema=False)
    def root_redirect() -> RedirectResponse:
        if dashboard_dir.exists():
            return RedirectResponse(url="/dashboard")
        return RedirectResponse(url="/docs")

    @app.get("/v1/health", response_model=HealthResponse)
    def health_check() -> HealthResponse:
        return HealthResponse(status="ok", service="subway-surf-motion-api")

    @app.get("/v1/config", dependencies=[Depends(guard)])
    def get_runtime_config() -> dict[str, Any]:
        data: dict[str, Any] = cfg.to_public_dict()
        data["active_profile"] = profiles.get_active_profile_name()
        return data

    @app.get("/v1/profiles", dependencies=[Depends(guard)], response_model=ProfileListResponse)
    def list_profiles() -> dict[str, Any]:
        active = profiles.get_active_profile_name()
        return {
            "active": active,
            "items": [p.to_dict() for p in profiles.list_profiles()],
        }

    @app.get("/v1/profiles/{name}", dependencies=[Depends(guard)])
    def get_profile(name: str) -> dict[str, Any]:
        try:
            profile = profiles.get_profile(name)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        return profile.to_dict()

    @app.put(
        "/v1/profiles/{name}",
        dependencies=[Depends(guard)],
        response_model=ProfileActionResponse,
    )
    def upsert_profile(name: str, payload: ProfilePayload) -> ProfileActionResponse:
        try:
            profile = Profile(
                name=name,
                description=payload.description,
                left_bound=payload.left_bound,
                right_bound=payload.right_bound,
                detection_confidence=payload.detection_confidence,
                presence_confidence=payload.presence_confidence,
                tracking_confidence=payload.tracking_confidence,
                cooldown_ms=payload.cooldown_ms,
            )
            profile.validate()
            saved = profiles.save_profile(profile)
            return ProfileActionResponse(status="saved", profile=saved.to_dict())
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

    @app.post(
        "/v1/profiles/{name}/activate",
        dependencies=[Depends(guard)],
        response_model=ProfileActionResponse,
    )
    def activate_profile(name: str) -> ProfileActionResponse:
        try:
            profile = profiles.activate_profile(name)
            return ProfileActionResponse(status="activated", profile=profile.to_dict())
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

    @app.get("/v1/telemetry", dependencies=[Depends(guard)], response_model=TelemetryResponse)
    def get_telemetry(limit: int = 30) -> TelemetryResponse:
        latest = telemetry.latest()
        return TelemetryResponse(
            latest=latest.to_dict() if latest else None,
            history=telemetry.history(limit=limit),
        )

    return app


def run_api_server(config: AppConfig) -> None:
    app = create_api_app(config=config)
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    run_api_server(load_config())
