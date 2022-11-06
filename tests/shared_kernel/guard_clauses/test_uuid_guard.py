import uuid

import pytest

from shared_kernel.guard_clauses.uuid_guard import is_valid_uuid


@pytest.mark.parametrize("not_a_uuid4", [123, "abc", {"heaven": "is", "a": "halfpipe"}])
def test_is_not_valid_uuid(not_a_uuid4):
    assert not is_valid_uuid(not_a_uuid4)


@pytest.mark.parametrize(
    "a_uuid4",
    [
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        str(uuid.uuid4()),
    ],
)
def test_is_valid_uuid(a_uuid4):
    assert is_valid_uuid(a_uuid4)
