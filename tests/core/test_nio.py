#!/usr/bin/env python3
from unittest.mock import call, patch

from schmetterling.core.nio import rm_paths


@patch("schmetterling.core.nio.rmdir")
@patch("schmetterling.core.nio.rmtree")
def test_rm_paths(mock_rmtree, mock_rmdir):
    with patch(
        "schmetterling.core.nio.walk",
        return_value=[("foo", None, None), ("bar", "dir_names", "files")],
    ):
        assert rm_paths(["p1", "p2"], "root") == ["p1", "p2"]
        assert mock_rmtree.mock_calls == [call("p1"), call("p2")]
        assert mock_rmdir.mock_calls == [call("foo")]
