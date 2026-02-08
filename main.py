from __future__ import annotations

import argparse
import logging
import threading

import uvicorn

from src.api.app import create_api_app, run_api_server
from src.app.runner import VirtualControllerApp
from src.utils.config import load_config
from src.utils.logger import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Subway Surfers gesture controller with API and dashboard support."
    )
    parser.add_argument(
        "--mode",
        choices=["controller", "api", "all"],
        default="controller",
        help="Execution mode.",
    )
    parser.add_argument("--camera-index", type=int, default=None, help="Override camera index.")
    parser.add_argument("--profile", type=str, default=None, help="Activate profile before start.")
    parser.add_argument("--api-host", type=str, default=None, help="API host override.")
    parser.add_argument("--api-port", type=int, default=None, help="API port override.")
    parser.add_argument(
        "--disable-auto-focus",
        action="store_true",
        help="Disable game window auto focus.",
    )
    parser.add_argument("--log-level", type=str, default=None, help="Override log level.")
    return parser.parse_args()


def _override_config(config, args: argparse.Namespace):
    if args.camera_index is not None:
        config.camera_index = args.camera_index
    if args.disable_auto_focus:
        config.auto_focus_window = False
    if args.api_host:
        config.api_host = args.api_host
    if args.api_port:
        config.api_port = args.api_port
    if args.log_level:
        config.log_level = args.log_level.upper()
    return config


def _start_api_background(config) -> threading.Thread:
    app = create_api_app(config=config)
    thread = threading.Thread(
        target=uvicorn.run,
        kwargs={
            "app": app,
            "host": config.api_host,
            "port": config.api_port,
            "log_level": config.log_level.lower(),
        },
        daemon=True,
    )
    thread.start()
    return thread


def main() -> None:
    args = parse_args()
    config = _override_config(load_config(), args)
    configure_logging(config.log_level, config.logs_dir)
    logger = logging.getLogger("main")

    if args.mode == "api":
        logger.info("Starting in API mode on %s:%s", config.api_host, config.api_port)
        run_api_server(config)
        return

    if args.mode == "all":
        logger.info("Starting API in background on %s:%s", config.api_host, config.api_port)
        _start_api_background(config)

    app = VirtualControllerApp(config)
    if args.profile:
        try:
            app.profile = app.profile_service.activate_profile(args.profile)
        except (FileNotFoundError, ValueError) as exc:
            logger.warning("Could not activate profile '%s': %s", args.profile, exc)
    app.run()


if __name__ == "__main__":
    main()

