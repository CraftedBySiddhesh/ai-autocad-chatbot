from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.cli.executor import execute_commands, load_commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI assisted CAD command line interface")
    parser.add_argument("--cmd", type=str, help="Single natural language command to execute")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/cli_output.dxf"),
        help="Destination DXF file path",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable LLM parsing and rely solely on deterministic rules",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Do not prompt for missing information; always use defaults",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    commands = load_commands(args.cmd, sys.stdin)
    if not commands:
        raise SystemExit("No commands provided")

    try:
        output = execute_commands(
            commands,
            output=args.out,
            enable_ai=not args.no_ai,
            interactive=not args.non_interactive,
        )
    except RuntimeError as exc:  # pragma: no cover - user feedback path
        print(f"Error: {exc}")
        raise SystemExit(2) from exc

    print(f"DXF saved to: {output}")


if __name__ == "__main__":
    main()
