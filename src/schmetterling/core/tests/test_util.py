#!/usr/bin/env python3

from schmetterling.core.util import merge_dicts


def test_merge_dicts():
    assert {"a": 2, "b": 2, "c": 3} == merge_dicts({"a": 1, "b": 2}, {"a": 2, "c": 3})
    merged = merge_dicts({"a": 1, "b": 2}, {"a": 2, "c": 3}, True)
    assert 3 == len(merged)
    assert 2 == len([v for v in merged if v == 2])
    assert 1 == len([v for v in merged if v == 3])
