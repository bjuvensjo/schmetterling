#!/usr/bin/env python3
from unittest.mock import MagicMock, call, patch

from schmetterling.build.state import Build, BuildState
from schmetterling.build_status.bitbucket import (
    get_bitbucket_repos,
    get_build_state,
    get_build_url,
    get_log_file,
    is_sub_url,
    set_single_status,
    set_status,
)
from schmetterling.log.state import LogState
from schmetterling.setup.state import SetupState


def test_get_bitbucket_repos():
    bitbucket_repos = [
        MagicMock(clone_url="http://myorg.com/stash/r1"),
        MagicMock(clone_url="http://myorg.com/stash/r2"),
    ]
    non_bitbucket_repos = [
        MagicMock(clone_url="http://myorg.com/nonstash/r1"),
        MagicMock(clone_url="http://myorg.com/nonstash/r2"),
    ]
    assert get_bitbucket_repos([], "http://myorg.com/stash") == []
    assert (
        get_bitbucket_repos(
            [1, SetupState("step", bitbucket_repos + non_bitbucket_repos), ""],
            "http://myorg.com/stash",
        )
        == bitbucket_repos
    )


def test_get_build_state():
    builds = [
        MagicMock(path="p1", status="success", timestamp="1"),
        MagicMock(path="p2", status="failure", timestamp="2"),
        MagicMock(path="p3", status="success", timestamp="1"),
    ]
    repos = [
        MagicMock(path="p1"),
        MagicMock(path="p2"),
        MagicMock(path="p3"),
        MagicMock(path="p4"),
    ]
    assert get_build_state([], [], "1") == []
    assert get_build_state([BuildState("step", builds)], repos, "1") == list(
        zip([repos[0], repos[2]], [b.status for b in builds if b.timestamp == "1"])
    )


def test_get_build_url():
    expected = (
        "http://10.20.30.40:8080/logs/delivery/schmetterling-20180903T103137.954036.log"
    )
    assert (
        get_build_url(
            "/Users/me/schmetterling/logs/delivery/schmetterling-20180903T103137.954036.log",
            "http",
            "10.20.30.40",
            8080,
            "/Users/me/schmetterling",
        )
        == expected
    )
    assert (
        get_build_url(
            "/Users/me/schmetterling/logs/delivery/schmetterling-20180903T103137.954036.log",
            "http",
            "10.20.30.40",
            8080,
            "/Users/me/schmetterling/",
        )
        == expected
    )


def test_get_log_file():
    assert (
        get_log_file(
            [
                1,
                LogState(
                    "step",
                    "/Users/me/schmetterling/logs/delivery/schmetterling-20180903T103137.954036.log",
                ),
                "",
            ]
        )
        == "/Users/me/schmetterling/logs/delivery/schmetterling-20180903T103137.954036.log"
    )
    assert not get_log_file([1, ""])


def test_is_sub_url():
    assert is_sub_url(
        "http://me@myorg.com/stash/scm/ztest/bar.git", "http://myorg.com/stash"
    )
    assert is_sub_url(
        "http://myorg.com/stash/scm/ztest/bar.git", "http://myorg.com/stash"
    )
    assert not is_sub_url(
        "http://me@myorg.com/stash/scm/ztest/bar.git", "http://yourorg.com/stash"
    )
    assert not is_sub_url(
        "http://myorg.com/stash/scm/ztest/bar.git", "http://yourorg.com/stash"
    )


def test_set_single_status():
    develop_branch = MagicMock()
    develop_branch.configure_mock(
        name="develop", head="develop_head"
    )  # To be able to set name attribute
    master_branch = MagicMock()
    master_branch.configure_mock(name="master", head="master_head")
    repo = MagicMock(setup_branch="develop", branches=[develop_branch, master_branch])
    with patch("schmetterling.build_status.bitbucket.call", return_value=204) as m:
        assert set_single_status("build_url", (repo, Build.SUCCESS)) == (
            repo,
            "develop_head",
            "SUCCESSFUL",
            "build_url",
            204,
        )
        assert m.mock_calls == [
            call(
                "/rest/build-status/1.0/commits/develop_head",
                {"state": "SUCCESSFUL", "key": "develop_head", "url": "build_url"},
                "POST",
                only_response_code=True,
            )
        ]


def test_set_status():
    with patch(
        "schmetterling.build_status.bitbucket.set_single_status", return_value=1
    ) as m:
        assert set_status([], "build_url") == []
        assert m.mock_calls == []

    with patch(
        "schmetterling.build_status.bitbucket.set_single_status", return_value=1
    ) as m:
        assert set_status([1, 2], "build_url") == [1, 1]
        assert m.mock_calls == [call("build_url", 1), call("build_url", 2)]
