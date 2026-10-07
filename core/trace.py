from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class TraceContext:
    execution_id: str
    created_at: str


def new_trace() -> TraceContext:
    return TraceContext(
        execution_id=str(uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
    )