#!/usr/bin/env python3
from vang.core.core import pmap
from vang.core.core import select_keys

from schmetterling.build.state import Build
from schmetterling.build.state import BuildState
from schmetterling.core.git import get_commit
from schmetterling.core.git import get_tag
from schmetterling.core.git import push
from schmetterling.core.log import log_params_return
from schmetterling.push.state import PushState
from schmetterling.push.state import Repo


@log_params_return('debug')
def create_state(pushed_repos):
    return PushState(__name__, [Repo(**r) for r in pushed_repos])


@log_params_return('debug')
def do_push(success_builds):
    @log_params_return('debug')
    def f(build):
        repo_dir = build['path']
        push(repo_dir)
        head_tag = get_tag(repo_dir)
        if head_tag:
            push(repo_dir, ref=head_tag)
        return dict(build, commit=get_commit(repo_dir), tag=head_tag)

    return pmap(f, success_builds)


@log_params_return('debug')
def get_success_builds(state):
    return [
        select_keys(b.__dict__, ['project', 'name', 'path']) for s in state
        if isinstance(s, BuildState) for b in s.builds
        if b.status == Build.SUCCESS
    ]


# TODO Use Tag_state?
@log_params_return('info')
def execute(state):
    success_builds = get_success_builds(state)
    pushed_repos = do_push(success_builds)
    push_state = create_state(pushed_repos)
    return push_state
