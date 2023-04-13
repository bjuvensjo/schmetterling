#!/usr/bin/env python3
from unittest.mock import call, patch

from schmetterling.core.git import get_commit, get_tag, git, push


def test_git():
    with patch("schmetterling.core.git.run_command", return_value=(0, "sha")) as m:
        assert git("repo_dir", "cmd", False) == (0, "sha")
        assert m.mock_calls == [
            call("cmd", check=False, cwd="repo_dir", return_output=True)
        ]


def test_get_commit():
    with patch("schmetterling.core.git.git", return_value=(0, "sha")) as m:
        assert get_commit("repo_dir", "ref") == "sha"
        assert m.mock_calls == [
            call(
                "repo_dir",
                "git rev-list --max-count=1 ref",
            )
        ]


def test_get_tag():
    with patch("schmetterling.core.git.git", return_value=(0, "tag")) as m:
        assert get_tag("repo_dir", "ref") == "tag"
        assert m.mock_calls == [
            call(
                "repo_dir",
                "git tag -l --points-at ref",
                False,
            )
        ]
    with patch("schmetterling.core.git.git", return_value=(0, "")):
        assert not get_tag("repo_dir", "ref")
    with patch("schmetterling.core.git.git", return_value=(0, None)):
        assert not get_tag("repo_dir", "ref")


def test_push():
    with patch("schmetterling.core.git.git", return_value=(0, "push")) as m:
        assert push("repo_dir", "origin", "ref") == "push"
        assert m.mock_calls == [
            call(
                "repo_dir",
                "git push origin ref",
            )
        ]
