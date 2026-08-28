from __future__ import annotations

import argparse
import asyncio
import json
import sys

from recruiter_agent.config import get_settings
from recruiter_agent.pipeline.orchestrator import Orchestrator
from recruiter_agent.utils.logging import configure_logging, get_logger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Process recruiter emails, match resume, and draft replies."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Fetch and process recruiter emails")
    run_parser.add_argument(
        "--max-emails",
        type=int,
        default=50,
        help="Maximum emails to fetch per run (default: 50)",
    )

    subparsers.add_parser("status", help="Show agent status")
    return parser


async def async_main(args: argparse.Namespace) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    log = get_logger("main")

    if settings.auto_send:
        log.error("auto_send_disabled_by_design", message="AUTO_SEND must remain false.")
        return 1

    orchestrator = Orchestrator(settings)

    if args.command == "run":
        stats = await orchestrator.run(max_emails=args.max_emails)
        print(json.dumps(stats, indent=2))
        return 0

    if args.command == "status":
        status = await orchestrator.status()
        print(json.dumps(status, indent=2))
        return 0

    return 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(asyncio.run(async_main(args)))


if __name__ == "__main__":
    main()
