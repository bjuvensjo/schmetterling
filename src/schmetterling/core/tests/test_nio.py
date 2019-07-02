#!/usr/bin/env python3
from unittest.mock import call, patch

from schmetterling.core.nio import rm_paths


@patch('schmetterling.core.nio.rmdir')
@patch('schmetterling.core.nio.rmtree')
def test_rm_paths(mock_rmtree, mock_rmdir):
    with patch(
            'schmetterling.core.nio.walk',
            return_value=[('foo', None, None), ('bar', 'dir_names', 'files')],
    ):
        assert ['p1', 'p2'] == rm_paths(['p1', 'p2'], 'root')
        assert [call('p1'), call('p2')] == mock_rmtree.mock_calls
        assert [call('foo')] == mock_rmdir.mock_calls
