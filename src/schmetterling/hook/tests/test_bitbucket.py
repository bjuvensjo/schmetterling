#!/usr/bin/env python3
from unittest.mock import MagicMock, call, patch

from schmetterling.hook.bitbucket import add_hook
from schmetterling.hook.bitbucket import create_repo_specs
from schmetterling.hook.bitbucket import execute
from schmetterling.hook.bitbucket import get_repos


@patch("schmetterling.hook.bitbucket.enable_web_hook", return_value="enable_web_hook")
def test_add_hook(mock_enable_web_hook):
    assert [
        {"hook": "hook", "name": "r1", "project": "project"},
        {"hook": "hook", "name": "r2", "project": "project"},
    ] == add_hook(
        [
            {"project": "project", "name": "r1"},
            {"project": "project", "name": "r2"},
        ],
        "hook",
    )
    assert [
        call([("project", "r1"), ("project", "r2")], "hook")
    ] == mock_enable_web_hook.mock_calls


def test_create_repo_specs():
    assert [("project", "r1"), ("project", "r2")] == create_repo_specs(
        [
            {"project": "project", "name": "r1"},
            {"project": "project", "name": "r2"},
        ]
    )


def test_get_repos():
    m = MagicMock()
    m.__dict__ = {"project": "project", "name": "name", "path": "path"}
    state = [MagicMock(repos=[m])]
    with patch("schmetterling.hook.bitbucket.isinstance", return_value=True):
        assert [{"name": "name", "path": "path", "project": "project"}] == get_repos(
            state
        )


@patch("schmetterling.hook.bitbucket.create_state", return_value="create_state")
@patch("schmetterling.hook.bitbucket.add_hook", return_value="add_hook")
@patch("schmetterling.hook.bitbucket.get_repos", return_value="repos")
def test_execute(mock_get_repos, mock_add_hook, mock_create_state):
    assert "create_state" == execute("state", **{"hook": "hook"})
    assert [call("state")] == mock_get_repos.mock_calls
    assert [call("repos", "hook")] == mock_add_hook.mock_calls
    assert [call("add_hook")] == mock_create_state.mock_calls
