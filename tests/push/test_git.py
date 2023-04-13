from unittest.mock import MagicMock, call, patch

from schmetterling.build.state import Build
from schmetterling.push.git import create_state, do_push, execute, get_success_builds
from schmetterling.push.state import PushState, Repo


def test_create_state():
    assert PushState(
        "schmetterling.push.git",
        [
            Repo(
                "project",
                "name",
                "path",
                "commit",
                "tag",
            )
        ],
    ) == create_state(
        [
            {
                "project": "project",
                "name": "name",
                "path": "path",
                "commit": "commit",
                "tag": "tag",
            }
        ]
    )


@patch("schmetterling.push.git.get_commit", return_value="commit")
@patch("schmetterling.push.git.get_tag", return_value="tag")
@patch("schmetterling.push.git.push")
def test_do_push(mock_push, mock_get_tag, mock_get_commit):
    assert do_push([{"path": "path"}]) == [
        {"commit": "commit", "path": "path", "tag": "tag"}
    ]
    assert mock_push.mock_calls == [call("path"), call("path", ref="tag")]
    assert mock_get_tag.mock_calls == [call("path")]
    assert mock_get_commit.mock_calls == [call("path")]


def test_get_success_builds():
    m = MagicMock()
    m.__dict__ = {
        "project": "project",
        "name": "name",
        "path": "path",
        "status": Build.SUCCESS,
    }
    state = [MagicMock(builds=[m])]
    with patch("schmetterling.push.git.isinstance", return_value=True):
        assert get_success_builds(state) == [
            {"name": "name", "path": "path", "project": "project"}
        ]


@patch("schmetterling.push.git.create_state", return_value="push_state")
@patch("schmetterling.push.git.do_push", return_value="pushed_repos")
@patch("schmetterling.push.git.get_success_builds", return_value="success_builds")
def test_execute(mock_get_success_builds, mock_do_push, mock_create_state):
    assert execute("state") == "push_state"
    assert mock_get_success_builds.mock_calls == [call("state")]
    assert mock_do_push.mock_calls == [call("success_builds")]
    assert mock_create_state.mock_calls == [call("pushed_repos")]
