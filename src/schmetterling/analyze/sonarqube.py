#!/usr/bin/env python3
from functools import partial
from logging import getLogger
from os import makedirs
from os.path import exists

from vang.core.core import pmap
from vang.pio.shell import run_command

from schmetterling.analyze.state import Analyze
from schmetterling.analyze.state import AnalyzeState
from schmetterling.build import maven
from schmetterling.build.state import Build
from schmetterling.core.log import log_params_return
from schmetterling.core.serialization import load
from schmetterling.state.state import StateState

log = getLogger(__name__)


@log_params_return('debug')
def analyze(
        log_dir,
        settings_file,
        sonar_plugin,
        sonar_url,
        sonar_auth_token,
        build,
):
    opts = f'-Dsonar.host.url={sonar_url} -Dsonar.login={sonar_auth_token}'
    log_path = f'{log_dir}/{build.name}.log'
    command = f'mvn -s {settings_file} {opts} {sonar_plugin}:sonar | tee {log_path}'
    return run_command(command, cwd=build.path, check=False, timeout=90), log_path, build


@log_params_return('debug')
def analyze_all(analyze_single, success_builds):
    return pmap(analyze_single, success_builds, processes=4)


@log_params_return('debug')
def create_state(sonar_analyzes, already_analyzed):
    def create_analyze(result_code, log_path, build):
        params = dict(
            build.__dict__,
            status=Analyze.SUCCESS if result_code == 0 else Analyze.FAILURE)
        return Analyze(**params)

    analyzes = [create_analyze(*a) for a in sonar_analyzes]
    return AnalyzeState(__name__, analyzes + already_analyzed)


@log_params_return('debug')
def get_success_builds(state):
    return [
        b for s in state if s.step == maven.__name__ for b in s.builds
        if b.status == Build.SUCCESS
    ]


@log_params_return('debug')
def init(log_dir):
    if not exists(log_dir):
        makedirs(log_dir)
    return log_dir


@log_params_return('debug')
def get_already_analyzed(success_builds, previous_state_file_path):
    sb_dict = {b.path: b.timestamp for b in success_builds}
    if previous_state_file_path:
        return [
            a for s in load(previous_state_file_path)
            if s.step == 'schmetterling.analyze.sonarqube' for a in s.analyzes
            if a.timestamp == sb_dict.get(a.path, None) and a.status == Analyze.SUCCESS
        ]
    return []


@log_params_return('debug')
def get_not_analyzed_builds(success_builds, already_analysed):
    return [
        b for b in success_builds
        if b.path not in [p.path for p in already_analysed]
    ]


@log_params_return('info')
def execute(
        state,
        log_dir,
        settings_file,
        sonar_plugin,
        sonar_url,
        sonar_auth_token,
):
    init(log_dir)
    success_builds = get_success_builds(state)
    previous_state_file_path = [s for s in state
                                if isinstance(s, StateState)][0].file_path
    already_analyzed = get_already_analyzed(success_builds,
                                            previous_state_file_path)
    not_analyzed_builds = get_not_analyzed_builds(success_builds,
                                                  already_analyzed)
    sonar_log_dir = f'{log_dir}/sonar'
    makedirs(sonar_log_dir, exist_ok=True)
    sonar_analyzes = analyze_all(
        partial(
            analyze,
            sonar_log_dir,
            settings_file,
            sonar_plugin,
            sonar_url,
            sonar_auth_token,
        ),
        not_analyzed_builds,
    )
    analyze_state = create_state(sonar_analyzes, already_analyzed)
    return analyze_state
