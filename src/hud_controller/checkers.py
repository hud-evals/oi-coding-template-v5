"""
Custom checkers for OI-style problems.

Each checker function receives:
- problem_id: The problem identifier
- input_data: The test case input as a string
- expected_output: The expected output as a string
- actual_output: The actual output from the solution as a string

Returns:
- Tuple of (passed: bool, message: str)
"""

import math
from typing import Callable

# Type alias for checker functions
CheckerFunc = Callable[[str, str, str, str], tuple[bool, str]]


def _parse_floats(s: str) -> list[float] | None:
    """Try to parse a string as a list of floats."""
    try:
        tokens = s.split()
        return [float(t) for t in tokens]
    except (ValueError, AttributeError):
        return None


def _floats_equal(a: float, b: float, rel_tol: float = 1e-6, abs_tol: float = 1e-9) -> bool:
    """Check if two floats are approximately equal."""
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def default_checker(problem_id: str, input_data: str, expected: str, actual: str) -> tuple[bool, str]:
    """
    Default checker with floating-point tolerance support.
    
    Compares outputs line by line:
    - If both lines parse as floats, compare with tolerance
    - Otherwise, compare as exact strings
    """
    expected_lines = expected.strip().split('\n')
    actual_lines = actual.strip().split('\n')
    
    if len(expected_lines) != len(actual_lines):
        return False, f"Line count mismatch: expected {len(expected_lines)}, got {len(actual_lines)}"
    
    for i, (exp_line, act_line) in enumerate(zip(expected_lines, actual_lines)):
        exp_line = exp_line.strip()
        act_line = act_line.strip()
        
        # Try float comparison first
        exp_floats = _parse_floats(exp_line)
        act_floats = _parse_floats(act_line)
        
        if exp_floats is not None and act_floats is not None and len(exp_floats) == len(act_floats):
            # Compare as floats
            for j, (e, a) in enumerate(zip(exp_floats, act_floats)):
                if not _floats_equal(e, a):
                    return False, f"Line {i+1}, token {j+1}: expected {e}, got {a}"
        else:
            # Compare as strings
            if exp_line != act_line:
                return False, f"Line {i+1}: expected '{exp_line}', got '{act_line}'"
    
    return True, "OK"


def checker_pastele(problem_id: str, input_data: str, expected: str, actual: str) -> tuple[bool, str]:
    """
    Custom checker for PASTELE problem.
    
    Verifies:
    - First line: colorfulness matches expected
    - All output crayons exist in input (using 256^3 counting array)
    - Each crayon not used more times than it appears in input
    - Recomputed colorfulness matches claimed colorfulness
    
    Uses O(N + K) time with O(256^3) space for fast lookups.
    """
    try:
        input_lines = input_data.strip().split('\n')
        expected_lines = expected.strip().split('\n')
        actual_lines = actual.strip().split('\n')
        
        # Parse input - count crayons in a 3D array
        n, k = map(int, input_lines[0].split())
        count = [[[0] * 256 for _ in range(256)] for _ in range(256)]
        for i in range(1, n + 1):
            r, g, b = map(int, input_lines[i].split())
            count[r][g][b] += 1
        
        # Check colorfulness matches expected
        expected_colorfulness = int(expected_lines[0].strip())
        if len(actual_lines) < 1:
            return False, "No output"
        
        try:
            actual_colorfulness = int(actual_lines[0].strip())
        except ValueError:
            return False, f"Invalid colorfulness: {actual_lines[0]}"
        
        if actual_colorfulness != expected_colorfulness:
            return False, f"Colorfulness mismatch: expected {expected_colorfulness}, got {actual_colorfulness}"
        
        # Check we have K crayons
        if len(actual_lines) < k + 1:
            return False, f"Expected {k} crayons, got {len(actual_lines) - 1}"
        
        # Parse output crayons, check they exist in input, and compute colorfulness
        min_r = min_g = min_b = 256
        max_r = max_g = max_b = -1
        
        for i in range(1, k + 1):
            parts = actual_lines[i].strip().split()
            if len(parts) != 3:
                return False, f"Invalid crayon format on line {i+1}"
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            
            if not (0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256):
                return False, f"Crayon ({r}, {g}, {b}) out of range"
            if count[r][g][b] <= 0:
                return False, f"Crayon ({r}, {g}, {b}) not available (not in input or already used)"
            
            # Decrement count to track usage
            count[r][g][b] -= 1
            
            min_r, max_r = min(min_r, r), max(max_r, r)
            min_g, max_g = min(min_g, g), max(max_g, g)
            min_b, max_b = min(min_b, b), max(max_b, b)
        
        # Verify recomputed colorfulness matches claimed
        computed_colorfulness = max(max_r - min_r, max_g - min_g, max_b - min_b)
        if computed_colorfulness != actual_colorfulness:
            return False, f"Computed colorfulness is {computed_colorfulness}, but claimed {actual_colorfulness}"
        
        return True, "OK"
        
    except Exception as e:
        return False, f"Checker error: {str(e)}"


def checker_rez(problem_id: str, input_data: str, expected: str, actual: str) -> tuple[bool, str]:
    """
    Custom checker for REZ problem.
    
    Verifies:
    - First line: N (number of cuts) matches expected
    - Next N lines: cuts are valid (on boundary) and divide cake into >= K pieces
    """
    try:
        # Parse input (K = target pieces)
        k = int(input_data.strip())
        
        expected_lines = expected.strip().split('\n')
        actual_lines = actual.strip().split('\n')
        
        # Parse expected N
        expected_n = int(expected_lines[0].strip())
        
        # Parse actual N
        if len(actual_lines) < 1:
            return False, "No output"
        
        try:
            actual_n = int(actual_lines[0].strip())
        except ValueError:
            return False, f"Invalid N: {actual_lines[0]}"
        
        # Check N matches expected
        if actual_n != expected_n:
            return False, f"N mismatch: expected {expected_n}, got {actual_n}"
        
        # Parse and validate cuts
        if len(actual_lines) < actual_n + 1:
            return False, f"Expected {actual_n} cuts, got {len(actual_lines) - 1}"
        
        cuts = []
        for i in range(1, actual_n + 1):
            try:
                parts = actual_lines[i].strip().split()
                if len(parts) != 4:
                    return False, f"Invalid cut format on line {i+1}"
                x1, y1, x2, y2 = map(int, parts)
                cuts.append((x1, y1, x2, y2))
            except (ValueError, IndexError):
                return False, f"Invalid cut on line {i+1}"
        
        # Validate each cut endpoint is on boundary
        def on_boundary(x, y):
            return max(abs(x), abs(y)) == 5000
        
        for i, (x1, y1, x2, y2) in enumerate(cuts):
            if not on_boundary(x1, y1):
                return False, f"Cut {i+1} endpoint ({x1}, {y1}) not on boundary"
            if not on_boundary(x2, y2):
                return False, f"Cut {i+1} endpoint ({x2}, {y2}) not on boundary"
        
        # Verify cuts create at least K pieces
        # For N non-parallel cuts through a convex region, max pieces = 1 + N + C(N,2) = 1 + N + N*(N-1)/2
        # But we need to actually count - for simplicity, use the formula for general position cuts
        # Pieces = 1 + N + (number of intersection points inside the cake)
        # For a simpler check: with N cuts in general position, pieces <= 1 + N + N*(N-1)/2
        # And we need pieces >= K
        
        # Count intersections inside the cake [-5000, 5000] x [-5000, 5000]
        def line_intersection(cut1, cut2):
            """Find intersection point of two line segments, if it exists inside the cake."""
            x1, y1, x2, y2 = cut1
            x3, y3, x4, y4 = cut2
            
            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(denom) < 1e-10:
                return None  # Parallel
            
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
            
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)
            
            # Check if inside cake (strictly inside, not on boundary)
            if -5000 < px < 5000 and -5000 < py < 5000:
                return (px, py)
            return None
        
        intersections = 0
        for i in range(len(cuts)):
            for j in range(i + 1, len(cuts)):
                if line_intersection(cuts[i], cuts[j]) is not None:
                    intersections += 1
        
        pieces = 1 + actual_n + intersections
        
        if pieces < k:
            return False, f"Cuts create only {pieces} pieces, need at least {k}"
        
        return True, "OK"
        
    except Exception as e:
        return False, f"Checker error: {str(e)}"


def _count_distinct_in_intervals(intervals: list[tuple[int, int]]) -> int:
    """
    Count distinct integers covered by a list of intervals.
    Uses interval merging in O(M log M) time.
    """
    if not intervals:
        return 0
    
    # Sort intervals by start point
    sorted_intervals = sorted(intervals)
    
    # Merge overlapping/adjacent intervals
    merged = []
    curr_start, curr_end = sorted_intervals[0]
    
    for start, end in sorted_intervals[1:]:
        if start <= curr_end + 1:  # Overlapping or adjacent
            curr_end = max(curr_end, end)
        else:
            merged.append((curr_start, curr_end))
            curr_start, curr_end = start, end
    merged.append((curr_start, curr_end))
    
    # Sum the lengths of merged intervals
    return sum(end - start + 1 for start, end in merged)


def checker_kolekcija(problem_id: str, input_data: str, expected: str, actual: str) -> tuple[bool, str]:
    """
    Custom checker for KOLEKCIJA problem.
    
    Verifies:
    - First line: disk accesses matches expected
    - Next M lines: valid intervals containing each song with length K
    
    Uses O(M log M) interval merging to count distinct songs.
    """
    try:
        input_lines = input_data.strip().split('\n')
        expected_lines = expected.strip().split('\n')
        actual_lines = actual.strip().split('\n')
        
        # Parse input
        first_line = input_lines[0].split()
        n, k = int(first_line[0]), int(first_line[1])
        m = int(input_lines[1].strip())
        
        songs = []
        for i in range(2, 2 + m):
            songs.append(int(input_lines[i].strip()))
        
        # Parse expected disk accesses
        expected_accesses = int(expected_lines[0].strip())
        
        # Parse actual output
        if len(actual_lines) < 1:
            return False, "No output"
        
        try:
            actual_accesses = int(actual_lines[0].strip())
        except ValueError:
            return False, f"Invalid disk accesses: {actual_lines[0]}"
        
        # Check disk accesses match
        if actual_accesses != expected_accesses:
            return False, f"Disk accesses mismatch: expected {expected_accesses}, got {actual_accesses}"
        
        # Parse intervals
        if len(actual_lines) < m + 1:
            return False, f"Expected {m} intervals, got {len(actual_lines) - 1}"
        
        intervals = []
        for i in range(1, m + 1):
            try:
                parts = actual_lines[i].strip().split()
                if len(parts) != 2:
                    return False, f"Invalid interval format on line {i+1}"
                a, b = int(parts[0]), int(parts[1])
                intervals.append((a, b))
            except (ValueError, IndexError):
                return False, f"Invalid interval on line {i+1}"
        
        # Validate each interval (O(M) checks)
        for i, (song, (a, b)) in enumerate(zip(songs, intervals)):
            # Check interval length
            if b - a + 1 != k:
                return False, f"Interval {i+1} has length {b - a + 1}, expected {k}"
            
            # Check interval bounds
            if a < 1 or b > n:
                return False, f"Interval {i+1} [{a}, {b}] out of bounds [1, {n}]"
            
            # Check song is in interval
            if not (a <= song <= b):
                return False, f"Song {song} not in interval [{a}, {b}]"
        
        # Count distinct songs using O(M log M) interval merging
        distinct_count = _count_distinct_in_intervals(intervals)
        
        # Check disk accesses count
        if distinct_count != actual_accesses:
            return False, f"Actual disk accesses should be {distinct_count}, claimed {actual_accesses}"
        
        return True, "OK"
        
    except Exception as e:
        return False, f"Checker error: {str(e)}"


# Registry mapping problem IDs to their custom checkers
CHECKER_REGISTRY: dict[str, CheckerFunc] = {
    "pastele": checker_pastele,
    "rez": checker_rez,
    "kolekcija": checker_kolekcija,
}


def get_checker(problem_id: str) -> CheckerFunc:
    """Get the appropriate checker for a problem."""
    return CHECKER_REGISTRY.get(problem_id, default_checker)

