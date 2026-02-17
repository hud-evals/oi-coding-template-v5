from dataclasses import dataclass


@dataclass
class OIProblemSpec:
    """Problem specification for OI-style algorithmic challenges."""

    id: str
    description: str
    difficulty: str = "easy"
    time_limit_seconds: int = 2
    memory_limit_mb: int = 256


OI_PROBLEM_REGISTRY: list[OIProblemSpec] = []
