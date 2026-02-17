"""OI-style algorithmic evaluation environment for HUD."""

import html
import logging
import os
import sys
from typing import Any

from hud import Environment

logger = logging.getLogger(__name__)
MCP_TESTING_MODE = os.environ.get("MCP_TESTING_MODE") in ["1", "true"]

sys.path.insert(0, "/mcp_server/src")

env = Environment("coding")


def _unescape(value: Any) -> Any:
    """Recursively unescape HTML entities in strings.

    Some LLM providers (notably xAI/Grok) return tool-call arguments
    with HTML-encoded characters, which corrupts source code.
    """
    if isinstance(value, str):
        return html.unescape(value)
    if isinstance(value, dict):
        return {k: _unescape(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_unescape(v) for v in value]
    return value


if MCP_TESTING_MODE:
    from hud_controller.tools.bash import BashTool
    from hud_controller.tools.edit import Command, EditTool
    from hud_controller.tools.base import ToolResult

    edit_tool = EditTool()
    bash_tool = BashTool()

    @env.tool(
        name="str_replace_based_edit_tool",
        description="Create and edit files. Use absolute paths.",
    )
    async def str_replace_based_edit_tool(
        *,
        command: Command,
        path: str,
        file_text: str | None = None,
        view_range: list[int] | None = None,
        old_str: str | None = None,
        new_str: str | None = None,
        insert_line: int | None = None,
    ) -> ToolResult:
        return await edit_tool(
            command=command,
            path=_unescape(path),
            file_text=_unescape(file_text),
            view_range=view_range,
            old_str=_unescape(old_str),
            new_str=_unescape(new_str),
            insert_line=insert_line,
        )

    @env.tool(
        name="bash",
        description="Run bash commands. Set restart=true to restart the session.",
    )
    async def bash(*, command: str | None = None, restart: bool = False) -> ToolResult:
        return await bash_tool(
            command=_unescape(command),
            restart=restart,
        )


if not MCP_TESTING_MODE:

    @env.tool(output_schema=None)
    async def setup_problem(problem_id: str, **kwargs: Any) -> str:
        """Setup the problem environment for the given task id."""
        logger.info("setup_problem called: %s", problem_id)

        if problem_id not in env._scenarios:
            return f"Unknown problem_id: {problem_id}. Known: {list(env._scenarios.keys())}"

        prompt = await env.run_scenario_setup(problem_id, {})
        if prompt is None:
            return f"Scenario '{problem_id}' setup returned no prompt"

        return kwargs.get("task_prompt") or prompt

    @env.tool(output_schema=None)
    async def grade_problem(problem_id: str, transcript: str = "", **kwargs: Any) -> dict:
        """Grade the problem by running the scenario's evaluate phase."""
        logger.info("grade_problem called: %s", problem_id)

        await env.submit(problem_id, transcript)
        result = await env.run_scenario_evaluate(problem_id)

        if result is None:
            return {
                "subscores": {"test_pass": 0.0},
                "weights": {"test_pass": 1},
                "metadata": {"error": "evaluation failed"},
            }

        subscores = {}
        weights = {}
        if result.subscores:
            for ss in result.subscores:
                subscores[ss.name] = ss.value
                weights[ss.name] = ss.weight
        else:
            subscores["test_pass"] = result.reward
            weights["test_pass"] = 1

        return {
            "subscores": subscores,
            "weights": weights,
            "metadata": {"score": result.reward, **(result.info or {})},
        }

# Register all OI scenarios
import tasks  # noqa: F401, E402
