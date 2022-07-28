#!/usr/bin/env python3

from vang.core.core import pmap_unordered
from vang.pio.shell import run_command

from schmetterling.core.git import get_commit, get_tag
from schmetterling.core.log import log_params_return
from schmetterling.setup.state import SetupState
from schmetterling.tag.state import Repo, Tag, TagState

TAG_PREFIX = "delivery"


@log_params_return("debug")
def create_state(tagged_repos):
    return TagState(
        __name__,
        [
            Repo(
                r["repo"].project,
                r["repo"].name,
                r["repo"].path,
                Tag(
                    r["tag"],
                    r["commit"],
                ),
            )
            for r in tagged_repos
        ],
    )


@log_params_return("debug")
def create_tag(timestamp):
    return f"{TAG_PREFIX}/{timestamp}"


@log_params_return("debug")
def get_repos(state):
    return [
        r
        for s in state
        if isinstance(s, SetupState)
        for r in s.repos
        if not has_delivery_tag(r)
    ]


@log_params_return("debug")
def has_delivery_tag(repo):
    head_tag = get_tag(repo.path)
    return bool(head_tag and head_tag.startswith(TAG_PREFIX))


@log_params_return("debug")
def do_tag(repos, tag):
    tag_cmd = f"git tag -a {tag} -m {tag}"

    @log_params_return("debug")
    def f(repo):
        rc, output = run_command(
            tag_cmd, return_output=True, cwd=repo.path, check=False
        )
        return {
            "repo": repo,
            "commit": get_commit(repo.path),
            "tag": tag,
            "success": rc == 0,
            "output": output,
        }

    return list(pmap_unordered(f, repos))


# TODO Consider from previous state if has already been tagged
# Really necessary to tag? Perhaps use head commit sha instead?
@log_params_return("info")
def execute(state, timestamp):
    repos = get_repos(state)
    tagged_repos = do_tag(repos, create_tag(timestamp))
    tag_state = create_state(tagged_repos)
    return tag_state
