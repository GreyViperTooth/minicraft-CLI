"""Lifecycle engine for minicraft."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from minicraft.errors import LifecycleError
from minicraft.models import Project
from minicraft.plugins import get_plugin


class Step(Enum):
    """Lifecycle steps in execution order."""

    PULL = "pull"
    BUILD = "build"
    STAGE = "stage"
    PRIME = "prime"


class ActionType(Enum):
    """The type of action to perform."""

    RUN = "run"
    SKIP = "skip"


@dataclass(frozen=True)
class Action:
    """A planned lifecycle action for a specific part."""

    step: Step
    action_type: ActionType
    part_name: str
    reason: str = ""


_STEP_ORDER = [Step.PULL, Step.BUILD, Step.STAGE, Step.PRIME]

_ACTION_MESSAGES: dict[Step, dict[ActionType, str]] = {
    Step.PULL: {ActionType.RUN: "Pull", ActionType.SKIP: "Skip pull"},
    Step.BUILD: {ActionType.RUN: "Build", ActionType.SKIP: "Skip build"},
    Step.STAGE: {ActionType.RUN: "Stage", ActionType.SKIP: "Skip stage"},
    Step.PRIME: {ActionType.RUN: "Prime", ActionType.SKIP: "Skip prime"},
}


def format_action_message(action: Action) -> str:
    """Format an action into a human-readable message."""
    message = f"{_ACTION_MESSAGES[action.step][action.action_type]} {action.part_name}"
    if action.reason:
        message += f" ({action.reason})"
    return message


class LifecycleManager:
    """Plans and executes lifecycle actions for a project."""

    def __init__(self, project: Project) -> None:
        self._project = project

    def plan(
        self,
        target_step: Step,
        part_names: list[str] | None = None,
    ) -> list[Action]:
        """Plan actions up to and including the target step.

        :param target_step: The step to execute up to.
        :param part_names: Optional list of parts to target. Defaults to all.
        :returns: An ordered list of Actions.
        """
        ordered_parts = self._resolve_order()

        if part_names:
            for name in part_names:
                if name not in self._project.parts:
                    raise LifecycleError(f"Part '{name}' not found in project.")

        target_index = _STEP_ORDER.index(target_step)
        steps_to_run = _STEP_ORDER[: target_index + 1]

        actions: list[Action] = []
        for step in steps_to_run:
            for part_name in ordered_parts:
                if part_names and part_name not in part_names:
                    actions.append(
                        Action(
                            step=step,
                            action_type=ActionType.SKIP,
                            part_name=part_name,
                            reason="not selected",
                        ),
                    )
                else:
                    actions.append(
                        Action(step=step, action_type=ActionType.RUN, part_name=part_name),
                    )

        return actions

    def execute(self, actions: list[Action], *, dry_run: bool = False) -> None:
        """Execute a list of planned actions.

        :param actions: The actions to execute.
        :param dry_run: If True, print the plan without executing.
        """
        for action in actions:
            if action.action_type == ActionType.SKIP:
                continue

            message = format_action_message(action)

            if dry_run:
                print(message)
                continue

            print(f"Execute: {message}")
            part_spec = self._project.parts[action.part_name]
            plugin = get_plugin(part_spec.plugin, action.part_name, part_spec)

            if action.step == Step.PULL:
                commands = plugin.get_pull_commands()
            elif action.step == Step.BUILD:
                commands = plugin.get_build_commands()
            elif action.step == Step.STAGE:
                commands = [f'echo "Staging {action.part_name}"']
            elif action.step == Step.PRIME:
                commands = [f'echo "Priming {action.part_name}"']

            for cmd in commands:
                print(f"  + {cmd}")

    def _resolve_order(self) -> list[str]:
        # a TODO for later: understand Kahn's algo -_-
        """Resolve part execution order via topological sort.

        :returns: Part names in dependency order.
        :raises LifecycleError: If a circular dependency is detected.
        """
        parts = self._project.parts
        in_degree: dict[str, int] = dict.fromkeys(parts, 0)
        graph: dict[str, list[str]] = {name: [] for name in parts}

        for name, spec in parts.items():
            for dep in spec.after:
                if dep not in parts:
                    raise LifecycleError(f"Part '{name}' depends on unknown part '{dep}'.")
                graph[dep].append(name)
                in_degree[name] += 1

        queue: list[str] = [name for name, degree in in_degree.items() if degree == 0]
        ordered: list[str] = []

        while queue:
            queue.sort()
            current = queue.pop(0)
            ordered.append(current)
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordered) != len(parts):
            raise LifecycleError("Circular dependency detected among parts.")

        return ordered
