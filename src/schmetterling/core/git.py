#!/usr/bin/env python3
from vang.pio.shell import run_command

from schmetterling.core.log import log_params_return


@log_params_return("debug")
def git(repo_dir, cmd, check=True):
    return run_command(cmd, return_output=True, cwd=repo_dir, check=check)


@log_params_return("debug")
def get_commit(repo_dir, ref="HEAD"):
    return git(repo_dir, f"git rev-list --max-count=1 {ref}")[1]


@log_params_return("debug")
def get_tag(repo_dir, ref="HEAD"):
    rc, output = git(repo_dir, f"git tag -l --points-at {ref}", False)
    return output or None


@log_params_return("debug")
def push(repo_dir, origin="origin", ref=""):
    return git(repo_dir, f"git push {origin} {ref}")[1]
