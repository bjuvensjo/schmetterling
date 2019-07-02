#!/usr/bin/env python3


def merge_dicts(base, update, values=False):
    merged = dict(base, **update)
    return list(merged.values()) if values else merged
