"""Command line helpers for DXF authoring demos."""

from __future__ import annotations

import argparse
from pathlib import Path

from .writer import demo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CAD demo utilities")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Generate a sample DXF showcasing basic primitives.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("out/demo_stage3.dxf"),
        help="Destination DXF path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.demo:
        path = demo(args.output)
        print(f"DXF demo written to {path}")
    else:
        raise SystemExit("Specify --demo to generate the sample DXF")


if __name__ == "__main__":
    main()
