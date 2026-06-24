"""CLI entry point for minicraft."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from minicraft.errors import MiniCraftError
from minicraft.lifecycle import ActionType, LifecycleManager, Step, format_action_message
from minicraft.project import load_project


def _parse_step(name: str) -> Step:
    """Map a subcommand name to a Step enum value."""
    step_map = {
        "pull": Step.PULL,
        "build": Step.BUILD,
        "stage": Step.STAGE,
        "prime": Step.PRIME,
    }
    return step_map[name]


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="minicraft",
        description="A miniature craft-parts lifecycle engine.",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        default=Path("project.yaml"),
        help="Path to the project YAML file. Defaults to 'project.yaml'.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the planned actions without executing.",
    )

    subparsers = parser.add_subparsers(dest="command")

    for cmd in ("pull", "build", "stage", "prime"):
        sub = subparsers.add_parser(cmd, help=f"Run the lifecycle up to the {cmd} step.")
        sub.add_argument(
            "parts",
            nargs="*",
            help="Specific parts to target. Defaults to all parts.",
        )

    clean_parser = subparsers.add_parser("clean", help="Remove build artifacts.")
    clean_parser.add_argument(
        "parts",
        nargs="*",
        help="Specific parts to clean. Defaults to all parts.",
    )

    return parser


def main() -> int:
    """Main entry point for the minicraft CLI."""
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "clean":
        print("Cleaning build artifacts...")
        return 0

    try:
        project = load_project(args.file)
    except MiniCraftError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    target_step = _parse_step(args.command)
    manager = LifecycleManager(project)

    try:
        part_names = args.parts if args.parts else None
        actions = manager.plan(target_step, part_names)
    except MiniCraftError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.dry_run:
        printed = False
        for action in actions:
            if action.action_type != ActionType.SKIP:
                print(format_action_message(action))
                printed = True
        if not printed:
            print("No actions to execute.")
    else:
        manager.execute(actions)

    return 0


if __name__ == "__main__":
    sys.exit(main())
