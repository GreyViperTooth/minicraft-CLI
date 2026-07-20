# minicraft

A miniature version of Canonical's [craft-parts](https://github.com/canonical/craft-parts)
lifecycle engine — small enough to read in one sitting, faithful enough to show
how the real thing works.

You describe a project as a set of named **parts** in a YAML file. minicraft
validates it, resolves the build order from each part's dependencies, and walks
the four craft-parts lifecycle steps — **pull → build → stage → prime** —
printing the commands each part's plugin would run at every step.

> minicraft is a lifecycle **planner/visualiser**: it prints the plan rather
> than running it. That keeps the focus on the interesting parts — schema
> validation, dependency ordering, and a plugin system.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```bash
# Run the lifecycle up to a step (pull | build | stage | prime)
uv run python -m minicraft --file examples/project.yaml build

# Preview the plan without executing
uv run python -m minicraft --file examples/project.yaml --dry-run prime

# Target specific parts (defaults to all)
uv run python -m minicraft -f examples/project.yaml build app
```

## Project file

```yaml
name: my-app
parts:
  assets:
    plugin: dump        # copy files, no build
    source: static/
  app:
    plugin: python      # create a venv and install dependencies
    source: .
    after:              # build order: assets before app
      - assets
```

- **`plugin`** — how the part is built. Built-in: `dump`, `python`.
- **`source`** — the part's source directory (default `.`).
- **`after`** — parts that must come first. minicraft topologically sorts these
  and rejects circular dependencies.

Unknown fields are rejected, so typos surface as clear validation errors.

## How it works

| Stage | Module | Responsibility |
|-------|--------|----------------|
| Validate | `models.py`, `project.py` | Parse the YAML and validate it into a typed `Project` (pydantic). |
| Plan | `lifecycle.py` | Topologically sort parts, then build the ordered list of actions up to the target step. |
| Execute | `lifecycle.py`, `plugins/` | For each action, resolve the part's plugin and print its commands. |

Plugins live in `src/minicraft/plugins/`. Each subclasses `Plugin` and returns
the commands to run for the pull/build steps. Adding one is a small class plus a
single entry in the plugin registry.

## Development

```bash
uv run ruff check      # lint
uv run pytest          # tests
```

## Status

Early and intentionally minimal. Executing steps prints commands rather than
running them; `clean` is a placeholder. Contributions and new plugins welcome.
