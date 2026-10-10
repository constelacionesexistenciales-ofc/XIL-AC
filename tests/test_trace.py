from uuid import UUID
from core.trace import new_trace

def test_trace_has_unique_uuid_and_utc_timestamp():
    first, second = new_trace(), new_trace()
    UUID(first.execution_id)
    assert first.execution_id != second.execution_id
    assert first.created_at.endswith("+00:00")
