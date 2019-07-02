#!/usr/bin/env python3
from json import load
from os.path import dirname

from vang.pio.shell import run_command

from schmetterling.build.state import Build, BuildState
from schmetterling.core.log import log_params_return


@log_params_return('debug')
def build(projects_dir):
    command = create_command(projects_dir)
    rc, output = run_command(
        command,
        return_output=True,
        cwd=projects_dir,
        check=False,
        timeout=None)

    return dict(build_result=read_build_result(projects_dir), output=output)


# TODO Handle settings and dependency cache
# TODO Only build updated?
# TODO Correct build command?
# TODO Use gradle wrapper
@log_params_return('debug')
def create_command(projects_dir):
    return ' '.join([
        'gradle build',
        f'-Dprojects_dir={projects_dir}',
        f'--project-cache-dir {projects_dir}',
        f'--init-script {dirname(__file__)}/init.gradle',
        f'--settings-file {dirname(__file__)}/settings.gradle',
        '--continue',
        '--configure-on-demand',
        '--parallel',
        '-q',
    ])


@log_params_return('debug')
def create_state(builds, timestamp):
    return BuildState(__name__, [
        Build(
            path=p,
            project=b['group'],
            status=Build.SUCCESS if b['result'] == 'SUCCESS' else Build.FAILURE,
            timestamp=timestamp,
            **b,
        ) for p, b in builds['build_result'].items()
    ])


@log_params_return('debug')
def read_build_result(build_dir):
    with open(
            f'{build_dir}/build_result.json',
            'rt',
            encoding='utf-8',
    ) as f:
        return load(f)


# TODO Add not builded coordinates to state?
# TODO Include latest commit and tags on that commit in build artifact
@log_params_return('info')
def execute(state, projects_dir, timestamp):
    builds = build(projects_dir)
    build_state = create_state(builds, timestamp)

    return build_state
