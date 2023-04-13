#!/usr/bin/env python3
from unittest.mock import MagicMock, call, patch

from schmetterling.hook.bitbucket import add_hook, create_repo_specs, execute, get_repos


@patch("schmetterling.hook.bitbucket.enable_web_hook", return_value="enable_web_hook")
def test_add_hook(mock_enable_web_hook):
    assert add_hook(
        [
            {"project": "project", "name": "r1"},
            {"project": "project", "name": "r2"},
        ],
        "hook",
    ) == [
        {"hook": "hook", "name": "r1", "project": "project"},
        {"hook": "hook", "name": "r2", "project": "project"},
    ]
    assert mock_enable_web_hook.mock_calls == [
        call([("project", "r1"), ("project", "r2")], "hook")
    ]


def test_create_repo_specs():
    assert create_repo_specs(
        [
            {"project": "project", "name": "r1"},
            {"project": "project", "name": "r2"},
        ]
    ) == [("project", "r1"), ("project", "r2")]


def test_get_repos():
    m = MagicMock()
    m.__dict__ = {"project": "project", "name": "name", "path": "path"}
    state = [MagicMock(repos=[m])]
    with patch("schmetterling.hook.bitbucket.isinstance", return_value=True):
        assert get_repos(state) == [
            {"name": "name", "path": "path", "project": "project"}
        ]


@patch("schmetterling.hook.bitbucket.create_state", return_value="create_state")
@patch("schmetterling.hook.bitbucket.add_hook", return_value="add_hook")
@patch("schmetterling.hook.bitbucket.get_repos", return_value="repos")
def test_execute(mock_get_repos, mock_add_hook, mock_create_state):
    assert execute("state", **{"hook": "hook"}) == "create_state"
    assert mock_get_repos.mock_calls == [call("state")]
    assert mock_add_hook.mock_calls == [call("repos", "hook")]
    assert mock_create_state.mock_calls == [call("add_hook")]
