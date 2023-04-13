#!/usr/bin/env python3

from schmetterling.core.util import merge_dicts


def test_merge_dicts():
    assert merge_dicts({"a": 1, "b": 2}, {"a": 2, "c": 3}) == {"a": 2, "b": 2, "c": 3}
    merged = merge_dicts({"a": 1, "b": 2}, {"a": 2, "c": 3}, True)
    assert len(merged) == 3
    assert len([v for v in merged if v == 2]) == 2
    assert len([v for v in merged if v == 3]) == 1
