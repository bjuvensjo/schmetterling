#!/usr/bin/env python3
from unittest.mock import call, patch

from schmetterling.core.git import get_commit
from schmetterling.core.git import get_tag
from schmetterling.core.git import git
from schmetterling.core.git import push


def test_git():
    with patch('schmetterling.core.git.run_command', return_value=(0, 'sha')) as m:
        assert (0, 'sha') == git('repo_dir', 'cmd', False)
        assert [call('cmd', check=False, cwd='repo_dir',
                     return_output=True)] == m.mock_calls


def test_get_commit():
    with patch('schmetterling.core.git.git', return_value=(0, 'sha')) as m:
        assert 'sha' == get_commit('repo_dir', 'ref')
        assert [call(
            'repo_dir',
            'git rev-list --max-count=1 ref',
        )] == m.mock_calls


def test_get_tag():
    with patch('schmetterling.core.git.git', return_value=(0, 'tag')) as m:
        assert 'tag' == get_tag('repo_dir', 'ref')
        assert [call(
            'repo_dir',
            'git tag -l --points-at ref',
            False,
        )] == m.mock_calls
    with patch('schmetterling.core.git.git', return_value=(0, '')):
        assert not get_tag('repo_dir', 'ref')
    with patch('schmetterling.core.git.git', return_value=(0, None)):
        assert not get_tag('repo_dir', 'ref')


def test_push():
    with patch('schmetterling.core.git.git', return_value=(0, 'push')) as m:
        assert 'push' == push('repo_dir', 'origin', 'ref')
        assert [call(
            'repo_dir',
            'git push origin ref',
        )] == m.mock_calls
