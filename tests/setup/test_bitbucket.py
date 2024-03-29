from unittest.mock import patch

from schmetterling.setup.bitbucket import (
    create_state,
    delete_non_included_repos,
    filter_repos,
)
from schmetterling.setup.state import Branch, Repo, SetupState


def test_create_state():
    assert SetupState("schmetterling.setup.bitbucket", None) == create_state(
        None,
        None,
        None,
        None,
        "develop",
    )
    assert create_state(
        [
            {
                "project": {"key": "project"},
                "slug": "name",
                "links": {"clone": [{"href": "clone_url"}]},
            }
        ],
        ["path"],
        [True],
        {
            ("project", "name"): [
                {"displayId": "develop", "isDefault": True, "latestCommit": "head"},
                {
                    "displayId": "feature/foo",
                    "isDefault": False,
                    "latestCommit": "head",
                },
            ]
        },
        "develop",
    ) == SetupState(
        "schmetterling.setup.bitbucket",
        [
            Repo(
                "project",
                "name",
                "clone_url",
                "path",
                [
                    Branch("develop", True, "head"),
                    Branch("feature/foo", False, "head"),
                ],
                "develop",
                Repo.STATUS_UPDATED,
            )
        ],
    )


@patch(
    "schmetterling.setup.bitbucket.get_cloned_repos_paths",
    return_value={"/foo/repo", "bar/repo"},
)
def test_delete_non_included_repos(mock_get_cloned_repos_paths):
    with patch(
        "schmetterling.setup.bitbucket.rm_paths", side_effect=lambda x, y: (x, y)
    ):
        assert delete_non_included_repos(["/bar/repo", "baz/repo"], "work_dir") == (
            {"/foo/repo", "bar/repo"},
            "work_dir",
        )


def test_filter_repos():
    repos = [
        {
            "project": {"key": "project"},
            "slug": "name1",
        },
        {
            "project": {"key": "project"},
            "slug": "name2",
        },
        {
            "project": {"key": "project"},
            "slug": "name3",
        },
    ]
    branches = {
        ("project", "name1"): [{"displayId": "develop"}],
        ("project", "name2"): [{"displayId": "master"}],
        ("project", "name3"): [{"displayId": "develop"}],
    }
    projects = {
        "project": {"includes": ["name1", "name2"]},
    }
    assert filter_repos(repos, branches, projects, "develop") == repos[:1]
