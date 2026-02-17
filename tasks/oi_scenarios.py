"""OI-style algorithmic challenge scenarios.

Each registered OI problem gets an @env.scenario() that:
1. Setup: returns the problem statement (inputs are already at /problems/)
2. Evaluate: runs the OI grading runner (compile + run against test cases)
"""

import logging
import sys

from env import env

# Ensure the hud_controller package is importable
sys.path.insert(0, "/mcp_server/src")

from hud_controller.oi_grading_runner import OIGradingRunner
from hud_controller.spec import OI_PROBLEM_REGISTRY, OIProblemSpec
from hud_controller.utils import import_submodules
import hud_controller.problems

logger = logging.getLogger(__name__)

# Import all problem modules to populate OI_PROBLEM_REGISTRY
import_submodules(hud_controller.problems)

# Template for OI problem prompts
OI_TEMPLATE = """You are solving an OI-style algorithmic challenge.

Your solution file should be written to: /workdir/{problem_id}.cpp or /workdir/{problem_id}.py

Note: Both Python and C++ solutions are accepted. However, Python solutions may run slower and could exceed time limits on larger test cases, potentially affecting your final score. C++ is recommended for optimal performance.

Your solution should:
- Read input from stdin
- Write output to stdout
- Handle all test cases within the time limit ({time_limit}s per test case)

Use the tools provided to complete the following task:

<PROBLEM>
{description}
</PROBLEM>
"""


def _register_scenario(spec: OIProblemSpec) -> None:
    """Register a single OI problem as a v5 scenario."""
    # Capture spec in closure scope (not as a function parameter, which would
    # be exposed to the MCP framework as a scenario argument)
    captured = spec

    @env.scenario(name=captured.id)
    async def _scenario():
        prompt = OI_TEMPLATE.format(
            problem_id=captured.id,
            description=captured.description,
            time_limit=captured.time_limit_seconds,
        )
        yield prompt

        runner = OIGradingRunner(
            problem_id=captured.id,
            time_limit_seconds=captured.time_limit_seconds,
        )
        result = runner.run_grading()

        logger.info(
            "Grading %s: %d/%d passed (score: %.2f)",
            captured.id, result.passed, result.total, result.score,
        )

        yield result.score


# Register all problems from the OI_PROBLEM_REGISTRY
for _spec in OI_PROBLEM_REGISTRY:
    _register_scenario(_spec)

logger.info("Registered %d OI scenarios", len(OI_PROBLEM_REGISTRY))
