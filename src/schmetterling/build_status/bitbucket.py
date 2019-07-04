#!/usr/bin/env python3
import logging
from functools import partial
from re import sub

from vang.bitbucket.api import call
from vang.core.core import pmap

from schmetterling.build.state import Build
from schmetterling.build.state import BuildState
from schmetterling.build_status.state import BuildStatusState
from schmetterling.build_status.state import Repo
from schmetterling.core.log import log_params_return
from schmetterling.log.state import LogState
from schmetterling.setup.state import SetupState

log = logging.getLogger(__name__)


@log_params_return('debug')
def create_state(statuses):
    repos = [
        Repo(
            repo.project, repo.name, repo.path, commit_id, build_url,
            Repo.STATUS_SUCCESS
            if state == STATUS_SUCCESSFUL else Repo.STATUS_FAILURE)
        for repo, commit_id, state, build_url, call_return_code in statuses
    ] if statuses else None
    return BuildStatusState(__name__, repos)


@log_params_return('debug')
def get_bitbucket_repos(state, url):
    return [
        r for s in state if isinstance(s, SetupState) for r in s.repos
        if is_sub_url(r.clone_url, url)
    ]


@log_params_return('debug')
def get_build_state(state, repos, timestamp):
    build_map = {
        b.path: b.status
        for s in state if isinstance(s, BuildState) for b in s.builds
        if b.timestamp == timestamp
    }
    return [(r, build_map[r.path]) for r in repos if r.path in build_map]


@log_params_return('debug')
def get_build_url(log_file, protocol, host, port, root):
    uri = '/'.join([s for s in log_file[len(root):].split('/') if s])
    return f'{protocol}://{host}:{port}/{uri}'


@log_params_return('debug')
def get_log_file(state):
    for s in state:
        if isinstance(s, LogState):
            return s.log_file
    # TODO Throw!!!
    return None


@log_params_return('debug')
def is_sub_url(clone_url, url):
    if '@' in clone_url:
        begin, end = clone_url.split('@', maxsplit=1)
        anonymous_clone_url = sub(r'(.*/).*', r'\1', begin, 1) + end
        return anonymous_clone_url.startswith(url)
    else:
        return clone_url.startswith(url)


STATUS_SUCCESSFUL = 'SUCCESSFUL'
STATUS_FAILED = 'FAILED'


@log_params_return('debug')
def set_single_status(build_url, build_state):
    repo, status = build_state
    state = STATUS_SUCCESSFUL if status == Build.SUCCESS else STATUS_FAILED
    commit_id = [b.head for b in repo.branches
                 if b.name == repo.setup_branch][0]
    request_data = {'state': state, 'key': commit_id, 'url': build_url}
    return repo, commit_id, state, build_url, call(
        f'/rest/build-status/1.0/commits/{commit_id}', request_data, 'POST', only_response_code=True)


@log_params_return('debug')
def set_status(build_state, build_url):
    return pmap(partial(set_single_status, build_url), build_state)


@log_params_return('info')
def execute(state, url, timestamp, build_log_params):
    repos = get_bitbucket_repos(state, url)
    build_state = get_build_state(state, repos, timestamp)
    log_file = get_log_file(state)
    build_url = get_build_url(log_file, **build_log_params)
    statuses = set_status(build_state, build_url)
    status_state = create_state(statuses)
    return status_state
