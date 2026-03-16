from typing import Any, Protocol


class ExecutionAdapter(Protocol):
    async def execute(self) -> dict[str, Any]:
        """Run an execution target and return normalized result payload."""
