# OI Coding Template

An evaluation environment for [HUD](https://hud.ai) that tests AI agents on competitive programming problems. The agent gets a problem description and access to bash + a file editor. It writes a C++ or Python solution, and we grade it by compiling and running it against hidden test cases.

## How it works

1. The agent receives a problem statement (e.g. "given N integers, count pairs sharing a digit")
2. It writes a solution to `/workdir/<problem_id>.cpp` or `.py`
3. We compile it, run it against 5-20 test cases, and score by % of tests passed

Expected outputs are locked behind a separate grading server running as a different user — the agent can't cheat by reading the answers.

## Quick start

```bash
# Install the HUD CLI and dependencies
pip install uv hud-python
uv sync

# Set your HUD API key
cp .env.example .env
# Edit .env with your key from hud.ai

# Build and deploy
hud build .     # local Docker build
hud deploy .    # deploy to HUD
```

Once deployed, go to your environment on [hud.ai](https://hud.ai). Click **New Taskset**, select your environment, choose the scenarios you want to run, pick an agent model, and hit **Run**.

## What's inside

```
env.py                          # HUD Environment — tools + scenarios
tasks/oi_scenarios.py           # Auto-registers all problems as scenarios
src/hud_controller/
  problems/oi.py                # 21 problem definitions (descriptions, time limits)
  oi_grading_runner.py          # Compiles solution, runs against test cases
  grading_server.py             # Secure Flask server for output comparison
  checkers.py                   # Custom checkers for multi-answer problems
  tools/                        # Bash and file editor for the agent
problems/
  <problem_id>/input/*.txt      # Test inputs (visible to agent)
  <problem_id>/output/*.txt     # Expected outputs (hidden at runtime)
Dockerfile.hud                  # Minimal image: Ubuntu + Python + g++
```

## Adding a problem

1. Add test data to `problems/<id>/input/` and `problems/<id>/output/` (files named `1.txt`, `2.txt`, etc.)
2. Register it in `src/hud_controller/problems/oi.py`:

```python
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="my_problem",
        description="Your problem statement here...",
        difficulty="medium",
        time_limit_seconds=2,
    )
)
```

3. If the problem has multiple valid outputs, add a custom checker in `src/hud_controller/checkers.py`

That's it — scenarios are auto-generated from the registry. Rebuild and redeploy to pick up the new problem.
