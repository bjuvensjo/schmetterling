#!/usr/bin/env python3
import logging
from functools import partial
from glob import glob
from os import makedirs
from os.path import exists, normpath, realpath
from pathlib import Path

from vang.core.core import is_included
from vang.core.core import pmap
from vang.pio.shell import run_command
from vang.tfs.get_branches import get_branches as vang_get_branches
from vang.tfs.get_repos import get_repos as vang_get_repos

from schmetterling.core.git import get_commit
from schmetterling.core.log import log_params_return
from schmetterling.core.nio import rm_paths
from schmetterling.core.serialization import load
from schmetterling.setup.state import Branch, Repo, SetupState
from schmetterling.state.state import StateState

log = logging.getLogger(__name__)


@log_params_return("debug")
def create_state(repos, paths, statuses, branches, setup_branch):
    return (
        SetupState(
            __name__,
            [
                Repo(
                    repo["project_spec"],
                    repo["name"],
                    repo["remoteUrl"],
                    path,
                    [
                        Branch(
                            b["name"],
                            b["name"] == repo["defaultBranch"].split("/")[-1],
                            b["objectId"],
                        )
                        for b in branches[f'{repo["project_spec"]}/{repo["name"]}']
                    ],
                    setup_branch,
                    Repo.STATUS_UPDATED if status else Repo.STATUS_UNCHANGED,
                )
                for repo, path, status in zip(repos, paths, statuses)
            ],
        )
        if repos
        else SetupState(__name__, None)
    )


@log_params_return("debug")
def delete_non_included_repos(repo_paths, work_dir):
    to_delete = get_cloned_repos_paths(work_dir) - set(repo_paths)
    return rm_paths(to_delete, work_dir)


@log_params_return("debug")
def filter_repos(repos, branches, projects, setup_branch):
    return [
        repo
        for repo in repos
        if is_included(
            repo["name"],
            **projects[repo["project_spec"]],
        )
        if has_branch(
            branches[f'{repo["project_spec"]}/{repo["name"]}'],
            setup_branch,
        )
    ]


@log_params_return("debug")
def get_branches(repos):
    return dict(
        vang_get_branches(repos=[f'{r["project_spec"]}/{r["name"]}' for r in repos])
    )


@log_params_return("debug")
def get_cloned_repos_paths(work_dir):
    return {
        str(Path(realpath(p)).parent)
        for p in glob(normpath(f"{work_dir}/**/.git"), recursive=True)
    }


@log_params_return("debug")
def get_repos(projects):
    repos = vang_get_repos(projects=projects.keys())
    return [dict(r, project_spec=p) for p, r in repos]


@log_params_return("debug")
def get_repo_paths(repos, work_dir):
    return [f'{work_dir}/{repo["project_spec"]}/{repo["name"]}' for repo in repos]


@log_params_return("debug")
def has_branch(branches, branch):
    return branch in [b["name"] for b in branches]


@log_params_return("debug")
def init(setup_dir, setup_branch):
    work_dir = f"{setup_dir}/{setup_branch}"
    makedirs(work_dir, exist_ok=True)
    return work_dir


@log_params_return("debug")
def update_repo(branches, setup_branch, repo, repo_path):
    head = get_commit(repo_path)
    if (
        head
        != [
            branch["objectId"]
            for branch in branches[f"{repo['project_spec']}/{repo['name']}"]
            if branch["name"] == setup_branch
        ][0]
    ):
        run_command(
            f"git fetch --all && git reset --hard origin/{setup_branch}", cwd=repo_path
        )
        return True
    return False


@log_params_return("debug")
def clone_repo(work_dir, setup_branch, repo, repo_path):
    run_command(f'git clone {repo["remoteUrl"]} -b {setup_branch} {repo_path}')
    return True


@log_params_return("debug")
def sync_repo(work_dir, branches, setup_branch, repo_and_repo_path):
    repo, repo_path = repo_and_repo_path
    return (
        update_repo(
            branches,
            setup_branch,
            repo,
            repo_path,
        )
        if exists(repo_path)
        else clone_repo(work_dir, setup_branch, repo, repo_path)
    )


@log_params_return("debug")
def sync_repos(repos, repo_paths, work_dir, branches, setup_branch):
    return pmap(
        partial(sync_repo, work_dir, branches, setup_branch), zip(repos, repo_paths)
    )


@log_params_return("debug")
def get_previous_state_repo_heads(previous_state):
    return {
        r.path: b.head
        for s in previous_state
        if s.step == "schmetterling.setup.tfs"
        for r in s.repos
        for b in r.branches
        if b.name == r.setup_branch
    }


@log_params_return("debug")
def get_repo_statuses(repo_paths, previous_state_file_path):
    if previous_state_file_path:
        previous_state_heads = get_previous_state_repo_heads(
            load(previous_state_file_path)
        )
        return [get_commit(p) != previous_state_heads.get(p, None) for p in repo_paths]
    return [True] * len(repo_paths)


@log_params_return("info")
def execute(state, url, username, password, setup_dir, setup_branch, projects):
    work_dir = init(setup_dir, setup_branch)
    all_repos = get_repos(projects)
    branches = get_branches(all_repos)
    repos = filter_repos(all_repos, branches, projects, setup_branch)
    repo_paths = get_repo_paths(repos, work_dir)
    delete_non_included_repos(repo_paths, work_dir)
    sync_repos(repos, repo_paths, work_dir, branches, setup_branch)
    previous_state_file_path = [s for s in state if isinstance(s, StateState)][
        0
    ].file_path
    repo_statuses = get_repo_statuses(repo_paths, previous_state_file_path)
    setup_state = create_state(repos, repo_paths, repo_statuses, branches, setup_branch)
    return setup_state
