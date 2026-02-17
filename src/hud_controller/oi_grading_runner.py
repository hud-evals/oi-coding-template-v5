#!/usr/bin/env python3
"""
OI-style grading runner for algorithmic challenges.

This script:
1. Detects solution file at /workdir/{problem_id}.cpp or /workdir/{problem_id}.py
2. Compiles C++ solutions with g++ -O2 -std=c++17
3. Runs solution against all test cases via the secure grading server
4. Uses HTTP API to submit outputs and get verdicts (prevents reward hacking)
5. Returns score based on passed/total test cases
"""

import logging
import os
import resource
import subprocess
from dataclasses import dataclass
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

# Memory limit for solutions (512 MB)
MEMORY_LIMIT_BYTES = 512 * 1024 * 1024

# Grading server configuration
GRADING_SERVER_URL = os.environ.get("GRADING_SERVER_URL", "http://127.0.0.1:5000")


def _set_resource_limits():
    """Set resource limits for child process: unlimited stack, limited memory."""
    # Set stack size to unlimited (needed for deep recursion)
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    # Set virtual memory limit
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))


@dataclass
class TestResult:
    """Result of a single test case."""

    test_id: str
    passed: bool
    status: str  # "AC", "WA", "TLE", "RE", "CE"
    time_ms: float
    stdout: str
    stderr: str
    message: str  # Message from grading server


@dataclass
class GradingResult:
    """Overall grading result."""

    score: float
    passed: int
    total: int
    language: str
    test_results: list[TestResult]
    compilation_error: str | None = None


class OIGradingRunner:
    """Handles the grading workflow for OI-style problems."""

    def __init__(
        self,
        problem_id: str,
        time_limit_seconds: int = 2,
        workdir: str = "/workdir",
        problems_dir: str = "/problems",
    ):
        """
        Initialize the OI grading runner.

        Args:
            problem_id: The problem identifier
            time_limit_seconds: Time limit per test case in seconds
            workdir: Directory where agent writes solutions
            problems_dir: Directory containing problem descriptions (inputs only accessible via API)
        """
        self.problem_id = problem_id
        self.time_limit_seconds = time_limit_seconds
        self.workdir = Path(workdir)
        self.problems_dir = Path(problems_dir)
        self.problem_path = self.problems_dir / problem_id
        self.input_dir = self.problem_path / "input"

    def _detect_solution(self) -> tuple[Path | None, str]:
        """
        Detect solution file and language.

        Returns:
            Tuple of (solution_path, language) or (None, "") if not found.
            Prefers C++ over Python if both exist.
        """
        cpp_path = self.workdir / f"{self.problem_id}.cpp"
        py_path = self.workdir / f"{self.problem_id}.py"

        if cpp_path.exists():
            return cpp_path, "cpp"
        elif py_path.exists():
            return py_path, "python"
        else:
            return None, ""

    def _compile_cpp(self, source_path: Path) -> tuple[bool, str]:
        """
        Compile C++ solution.

        Returns:
            Tuple of (success, error_message)
        """
        output_path = self.workdir / self.problem_id

        try:
            result = subprocess.run(
                [
                    "g++",
                    "-O2",
                    "-std=c++17",
                    "-o",
                    str(output_path),
                    str(source_path),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                return False, result.stderr
            return True, ""

        except subprocess.TimeoutExpired:
            return False, "Compilation timed out (>60s)"
        except Exception as e:
            return False, str(e)

    def _get_test_cases_from_api(self) -> list[str]:
        """
        Get list of test case IDs from the grading server API.

        Returns:
            Sorted list of test case IDs (e.g., ["1", "2", "3"])
        """
        try:
            response = requests.get(
                f"{GRADING_SERVER_URL}/list_tests/{self.problem_id}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("tests", [])
            else:
                logger.warning(f"Failed to get test list from API: {response.status_code}")
                return []
        except requests.RequestException as e:
            logger.warning(f"Failed to connect to grading server: {e}")
            return []

    def _get_test_cases_local(self) -> list[str]:
        """
        Fallback: Get list of test case IDs by scanning local input directory.
        This is used when grading server is not available.

        Returns:
            Sorted list of test case IDs (e.g., ["1", "2", "3"])
        """
        if not self.input_dir.exists():
            logger.warning(f"Input directory not found: {self.input_dir}")
            return []

        test_cases = []
        for f in self.input_dir.iterdir():
            if f.suffix == ".txt":
                test_cases.append(f.stem)

        # Sort numerically if possible, otherwise alphabetically
        try:
            test_cases.sort(key=lambda x: (0, int(x)) if x.isdigit() else (1, x))
        except ValueError:
            test_cases.sort()

        return test_cases

    def _get_test_cases(self) -> list[str]:
        """
        Get list of test case IDs.
        Tries API first, falls back to local directory scan.
        """
        # Try API first
        test_cases = self._get_test_cases_from_api()
        if test_cases:
            return test_cases
        
        # Fallback to local scan
        return self._get_test_cases_local()

    def _normalize_output(self, output: str) -> str:
        """
        Normalize output for comparison.
        - Strip trailing whitespace from each line
        - Strip trailing newlines
        - Normalize line endings
        """
        lines = output.replace("\r\n", "\n").split("\n")
        lines = [line.rstrip() for line in lines]
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines)

    def _grade_via_api(self, test_id: str, actual_output: str) -> tuple[bool, str]:
        """
        Submit output to grading server and get verdict.

        Args:
            test_id: Test case identifier
            actual_output: The solution's output

        Returns:
            Tuple of (passed, message)
        """
        try:
            response = requests.post(
                f"{GRADING_SERVER_URL}/grade",
                json={
                    "problem_id": self.problem_id,
                    "test_id": test_id,
                    "actual_output": actual_output
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("passed", False), data.get("message", "")
            else:
                data = response.json() if response.headers.get("content-type") == "application/json" else {}
                return False, data.get("message", f"API error: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Failed to connect to grading server: {e}")
            return False, f"Grading server error: {e}"

    def _run_test_case(self, test_id: str, executable: Path, language: str) -> TestResult:
        """
        Run solution against a single test case.

        Args:
            test_id: Test case identifier
            executable: Path to compiled binary or Python script
            language: "cpp" or "python"

        Returns:
            TestResult with pass/fail status and details
        """
        # Read input from local directory (agent has read access to inputs)
        input_file = self.input_dir / f"{test_id}.txt"

        if not input_file.exists():
            return TestResult(
                test_id=test_id,
                passed=False,
                status="RE",
                time_ms=0,
                stdout="",
                stderr=f"Input file not found: {input_file}",
                message="Input file not found",
            )

        # Build command
        if language == "cpp":
            cmd = [str(executable)]
        else:
            cmd = ["python3", str(executable)]

        # Run solution
        try:
            with open(input_file) as stdin_file:
                import time

                start_time = time.perf_counter()
                result = subprocess.run(
                    cmd,
                    stdin=stdin_file,
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit_seconds,
                    cwd=self.workdir,
                    preexec_fn=_set_resource_limits,
                )
                end_time = time.perf_counter()
                time_ms = (end_time - start_time) * 1000

            if result.returncode != 0:
                return TestResult(
                    test_id=test_id,
                    passed=False,
                    status="RE",
                    time_ms=time_ms,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    message=f"Runtime error (exit code {result.returncode})",
                )

            # Normalize output and submit to grading server
            actual_output = self._normalize_output(result.stdout)
            
            # Grade via API (secure - doesn't expose expected output)
            passed, message = self._grade_via_api(test_id, actual_output)

            if passed:
                return TestResult(
                    test_id=test_id,
                    passed=True,
                    status="AC",
                    time_ms=time_ms,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    message=message,
                )
            else:
                return TestResult(
                    test_id=test_id,
                    passed=False,
                    status="WA",
                    time_ms=time_ms,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    message=message,
                )

        except subprocess.TimeoutExpired:
            return TestResult(
                test_id=test_id,
                passed=False,
                status="TLE",
                time_ms=self.time_limit_seconds * 1000,
                stdout="",
                stderr=f"Time limit exceeded ({self.time_limit_seconds}s)",
                message="Time limit exceeded",
            )
        except Exception as e:
            return TestResult(
                test_id=test_id,
                passed=False,
                status="RE",
                time_ms=0,
                stdout="",
                stderr=str(e),
                message=str(e),
            )

    def run_grading(self) -> GradingResult:
        """
        Run the complete grading workflow.

        Returns:
            GradingResult with score and test details
        """
        logger.info(f"Starting OI grading for problem: {self.problem_id}")

        # Detect solution
        solution_path, language = self._detect_solution()

        if solution_path is None:
            logger.error(f"No solution found for {self.problem_id}")
            return GradingResult(
                score=0.0,
                passed=0,
                total=0,
                language="unknown",
                test_results=[],
                compilation_error=f"No solution file found. Expected {self.problem_id}.cpp or {self.problem_id}.py in {self.workdir}",
            )

        logger.info(f"Found {language} solution: {solution_path}")

        # Compile if C++
        executable = solution_path
        if language == "cpp":
            logger.info("Compiling C++ solution...")
            success, error = self._compile_cpp(solution_path)
            if not success:
                logger.error(f"Compilation failed: {error}")
                return GradingResult(
                    score=0.0,
                    passed=0,
                    total=0,
                    language=language,
                    test_results=[],
                    compilation_error=error,
                )
            executable = self.workdir / self.problem_id
            logger.info("Compilation successful")

        # Get test cases
        test_cases = self._get_test_cases()
        if not test_cases:
            logger.warning("No test cases found")
            return GradingResult(
                score=0.0,
                passed=0,
                total=0,
                language=language,
                test_results=[],
                compilation_error=f"No test cases found for problem {self.problem_id}",
            )

        logger.info(f"Found {len(test_cases)} test cases")

        # Run all test cases
        test_results = []
        passed = 0

        for test_id in test_cases:
            logger.info(f"Running test case {test_id}...")
            result = self._run_test_case(test_id, executable, language)
            test_results.append(result)

            if result.passed:
                passed += 1
                logger.info(f"  Test {test_id}: {result.status} ({result.time_ms:.1f}ms)")
            else:
                logger.info(f"  Test {test_id}: {result.status} ({result.time_ms:.1f}ms) - {result.message}")

        total = len(test_cases)
        score = passed / total if total > 0 else 0.0

        logger.info(f"Grading complete: {passed}/{total} tests passed (score: {score:.2f})")

        return GradingResult(
            score=score,
            passed=passed,
            total=total,
            language=language,
            test_results=test_results,
        )
