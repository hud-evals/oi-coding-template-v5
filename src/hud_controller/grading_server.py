#!/usr/bin/env python3
"""
Secure grading server for OI-style problems.

This server runs as a separate user (grader) and has exclusive access to test inputs
and expected outputs. The main agent process can only interact via HTTP API,
preventing reward hacking by reading expected outputs directly.

API:
    POST /grade - Grade a solution's output for a specific test case
    GET /list_tests/<problem_id> - List available test cases for a problem
    GET /health - Health check endpoint
"""

import logging
import os
from pathlib import Path

from flask import Flask, jsonify, request

from hud_controller.checkers import get_checker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Directories for test data (only accessible by grader user)
GRADING_DIR = Path(os.environ.get("GRADING_DIR", "/grading"))
INPUTS_DIR = GRADING_DIR / "inputs"
OUTPUTS_DIR = GRADING_DIR / "outputs"


def normalize_output(output: str) -> str:
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


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "grading-server"})


@app.route("/list_tests/<problem_id>", methods=["GET"])
def list_tests(problem_id: str):
    """
    List available test cases for a problem.
    
    Returns test IDs (without .txt extension) from the inputs directory.
    """
    input_dir = INPUTS_DIR / problem_id
    
    if not input_dir.exists():
        return jsonify({"error": f"Problem '{problem_id}' not found"}), 404
    
    tests = []
    for f in input_dir.iterdir():
        if f.suffix == ".txt":
            tests.append(f.stem)
    
    # Sort numerically if possible, otherwise alphabetically
    try:
        tests.sort(key=lambda x: (0, int(x)) if x.isdigit() else (1, x))
    except ValueError:
        tests.sort()
    
    return jsonify({"problem_id": problem_id, "tests": tests, "count": len(tests)})


@app.route("/grade", methods=["POST"])
def grade():
    """
    Grade a solution's output for a specific test case.
    
    Request body:
        {
            "problem_id": "pastele",
            "test_id": "1",
            "actual_output": "5\n10 20 30\n..."
        }
    
    Response:
        {
            "verdict": "AC" | "WA",
            "passed": true | false,
            "message": "OK" | "error description"
        }
    
    Security: Never returns actual input or expected output content.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"verdict": "WA", "passed": False, "message": "No JSON body provided"}), 400
        
        problem_id = data.get("problem_id")
        test_id = data.get("test_id")
        actual_output = data.get("actual_output", "")
        
        if not problem_id:
            return jsonify({"verdict": "WA", "passed": False, "message": "Missing problem_id"}), 400
        
        if not test_id:
            return jsonify({"verdict": "WA", "passed": False, "message": "Missing test_id"}), 400
        
        # Construct file paths
        input_file = INPUTS_DIR / problem_id / f"{test_id}.txt"
        output_file = OUTPUTS_DIR / problem_id / f"{test_id}.txt"
        
        # Check files exist
        if not input_file.exists():
            logger.warning(f"Input file not found: {input_file}")
            return jsonify({
                "verdict": "WA",
                "passed": False,
                "message": f"Test case '{test_id}' not found for problem '{problem_id}'"
            }), 404
        
        if not output_file.exists():
            logger.warning(f"Output file not found: {output_file}")
            return jsonify({
                "verdict": "WA",
                "passed": False,
                "message": f"Expected output not found for test '{test_id}'"
            }), 404
        
        # Read test data
        try:
            input_data = input_file.read_text()
            expected_output = output_file.read_text()
        except Exception as e:
            logger.error(f"Error reading test files: {e}")
            return jsonify({
                "verdict": "WA",
                "passed": False,
                "message": "Internal error reading test data"
            }), 500
        
        # Get appropriate checker for this problem
        checker = get_checker(problem_id)
        
        # Run the checker
        try:
            passed, message = checker(
                problem_id,
                input_data,
                expected_output,
                actual_output
            )
        except Exception as e:
            logger.error(f"Checker error for {problem_id}/{test_id}: {e}")
            return jsonify({
                "verdict": "WA",
                "passed": False,
                "message": f"Checker error: {str(e)}"
            })
        
        verdict = "AC" if passed else "WA"
        
        logger.info(f"Graded {problem_id}/{test_id}: {verdict}")
        
        return jsonify({
            "verdict": verdict,
            "passed": passed,
            "message": message
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in grade endpoint: {e}")
        return jsonify({
            "verdict": "WA",
            "passed": False,
            "message": "Internal server error"
        }), 500


def main():
    """Run the grading server."""
    host = os.environ.get("GRADING_HOST", "127.0.0.1")
    port = int(os.environ.get("GRADING_PORT", "5000"))
    
    logger.info(f"Starting grading server on {host}:{port}")
    logger.info(f"Inputs directory: {INPUTS_DIR}")
    logger.info(f"Outputs directory: {OUTPUTS_DIR}")
    
    # Check directories exist
    if not INPUTS_DIR.exists():
        logger.warning(f"Inputs directory does not exist: {INPUTS_DIR}")
    if not OUTPUTS_DIR.exists():
        logger.warning(f"Outputs directory does not exist: {OUTPUTS_DIR}")
    
    # Run with threading for concurrent requests
    app.run(host=host, port=port, threaded=True)


if __name__ == "__main__":
    main()

