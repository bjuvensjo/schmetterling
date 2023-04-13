from unittest.mock import MagicMock, call, patch

from schmetterling.setup.state import Repo as Setup_repo
from schmetterling.tag.git_delivery import (
    create_state,
    create_tag,
    do_tag,
    execute,
    get_repos,
    has_delivery_tag,
)
from schmetterling.tag.state import Repo, Tag, TagState


def test_create_state():
    assert create_state(
        [
            {
                "repo": Setup_repo("project", "name", None, "path", None, None, None),
                "tag": "tag",
                "commit": "commit",
            }
        ]
    ) == TagState(
        "schmetterling.tag.git_delivery",
        [
            Repo("project", "name", "path", Tag("tag", "commit")),
        ],
    )


def test_create_tag():
    assert create_tag("timestamp") == "delivery/timestamp"


def test_get_repos():
    state = [MagicMock(repos=["foo", "bar", "baz"])]

    with patch("schmetterling.tag.git_delivery.isinstance", return_value=True):
        with patch(
            "schmetterling.tag.git_delivery.has_delivery_tag", return_value=False
        ):
            assert get_repos(state) == ["foo", "bar", "baz"]
        with patch(
            "schmetterling.tag.git_delivery.has_delivery_tag", return_value=True
        ):
            assert get_repos(state) == []

    with patch("schmetterling.tag.git_delivery.isinstance", return_value=False):
        with patch(
            "schmetterling.tag.git_delivery.has_delivery_tag", return_value=False
        ):
            assert get_repos(state) == []


def test_has_delivery_tag():
    with patch(
        "schmetterling.tag.git_delivery.get_tag",
        return_value=None,
    ) as m:
        assert not has_delivery_tag(MagicMock(path="path"))
        assert m.mock_calls == [call("path")]

    with patch(
        "schmetterling.tag.git_delivery.get_tag",
        return_value="delivery",
    ) as m:
        assert has_delivery_tag(MagicMock(path="path"))


@patch("schmetterling.tag.git_delivery.get_commit", return_value=1)
@patch("schmetterling.tag.git_delivery.run_command", return_value=(0, "output"))
def test_do_tag(mock_run_command, mock_get_head_commit_id):
    setup_repo = Setup_repo(None, None, None, "path", None, None, None)
    assert do_tag([setup_repo], "tag") == [
        {
            "commit": 1,
            "output": "output",
            "repo": setup_repo,
            "success": True,
            "tag": "tag",
        }
    ]

    assert mock_run_command.mock_calls == [
        call("git tag -a tag -m tag", check=False, cwd="path", return_output=True)
    ]
    assert mock_get_head_commit_id.mock_calls == [call("path")]


@patch("schmetterling.tag.git_delivery.create_state", return_value="state")
@patch("schmetterling.tag.git_delivery.create_tag", return_value="tag")
@patch("schmetterling.tag.git_delivery.do_tag", return_value="tagged_repos")
@patch("schmetterling.tag.git_delivery.get_repos", return_value="repos")
def test_execute(
    mock_get_repos,
    mock_do_tag,
    mock_create_tag,
    mock_create_state,
):
    assert execute("state", "timestamp", **{}) == "state"
    assert mock_create_tag.mock_calls == [call("timestamp")]
    assert mock_create_state.mock_calls == [call("tagged_repos")]
    assert mock_do_tag.mock_calls == [call("repos", "tag")]
    assert mock_get_repos.mock_calls == [call("state")]
