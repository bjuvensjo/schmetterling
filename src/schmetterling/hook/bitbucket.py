#!/usr/bin/env python3
from vang.bitbucket.enable_webhooks import enable_web_hook
from vang.core.core import select_keys

from schmetterling.core.log import log_params_return
from schmetterling.hook.state import HookState
from schmetterling.hook.state import Repo
from schmetterling.setup.state import SetupState


# TODO Check response from enable_web_hook for successes?
@log_params_return("debug")
def add_hook(repos, hook):
    repo_specs = create_repo_specs(repos)
    enable_web_hook(repo_specs, hook)
    return [dict(r, hook=hook) for r in repos]


@log_params_return("debug")
def create_repo_specs(repos):
    return [(r["project"], r["name"]) for r in repos]


@log_params_return("debug")
def get_repos(state):
    return [
        select_keys(r.__dict__, ["project", "name", "path"])
        for s in state
        if isinstance(s, SetupState)
        for r in s.repos
    ]


@log_params_return("debug")
def create_state(hooked_repos):
    return HookState(__name__, [Repo(**r) for r in hooked_repos])


# TODO Consider from previous state if has already been hooked
@log_params_return("info")
def execute(state, hook):
    repos = get_repos(state)
    hooked_repos = add_hook(repos, hook)
    hook_state = create_state(hooked_repos)
    return hook_state
