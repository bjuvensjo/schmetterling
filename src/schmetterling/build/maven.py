#!/usr/bin/env python3
from logging import getLogger
from os import makedirs
from os.path import exists
from shutil import rmtree

from vang.maven.multi_module_project import get_pom
from vang.maven.pom import get_pom_info
from vang.maven.reactor_summary import get_summary
from vang.pio.shell import run_command

from schmetterling.build.state import Build, BuildState
from schmetterling.core.log import log_params_return
from schmetterling.core.serialization import load
from schmetterling.setup.state import Repo, SetupState
from schmetterling.state.state import StateState

log = getLogger(__name__)


@log_params_return('debug')
def build_multi_modules(multi_modules, repository_dir, settings_file,
                        logback_file):
    success_coordinates = []
    failure_coordinates = []
    for mm in multi_modules:
        build_modules = mm['updated']
        mvn_log = f'{mm["pom_dir"]}/mvn.log'
        command = create_command(
            build_modules,
            mvn_log,
            repository_dir,
            settings_file,
            logback_file,
        )
        run_command(command, cwd=mm['pom_dir'])
        mm_success_coordinates, mm_failure_coordinates = create_build_result(
            mm['coordinates'], build_modules, mvn_log)
        success_coordinates += mm_success_coordinates
        failure_coordinates += mm_failure_coordinates
    return success_coordinates, failure_coordinates


@log_params_return('debug')
def create_build_result(coordinates, build_modules, mvn_log):
    successes, failures = get_summary([mvn_log])
    success_coordinates = [
        c for c in coordinates if c['artifact_id'] in successes
        or f'{c["group_id"]}:{c["artifact_id"]}' in successes
    ]
    # Maven does not log all types of errors in the reactor summary so add all
    # modules to build failures that are not found as successes
    failure_coordinates = [
        c for c in coordinates
        if c['artifact_id'] in failures or f'{c["group_id"]}:{c["artifact_id"]}'
        in failures or (c in build_modules and c not in success_coordinates)
    ]
    return success_coordinates, failure_coordinates


@log_params_return('debug')
def create_command(build_modules, mvn_log, repository_dir, settings_file,
                   logback_file):
    java_opts = ' '.join([
        '-Dmaven.repo.local=' + repository_dir, '-s ' + settings_file,
        '-DcreateChecksum=true', '-Dfile.encoding=UTF-8',
        '-Dsun.jnu.encoding=UTF-8',
        '-Dlogback.configurationFile=' + logback_file
    ])
    plugins = 'javadoc:jar source:jar'
    build_modules_string = ','.join(
        [f'{m["group_id"]}:{m["artifact_id"]}' for m in build_modules])

    return ' '.join([
        'mvn',
        java_opts,
        '-B -amd -pl',
        build_modules_string,
        'clean install',
        plugins,
        '--fail-at-end | tee',
        mvn_log,
    ])


@log_params_return('debug')
def create_multi_modules(multi_modules):
    for mm in multi_modules:
        makedirs(mm['pom_dir'], exist_ok=True)
        with open(f'{mm["pom_dir"]}/pom.xml', 'wt', encoding='utf-8') as f:
            f.write(mm['pom_content'])


@log_params_return('debug')
def create_state(
        previous_builds,
        success_coordinates,
        failure_coordinates,
        timestamp,
):
    success_modules = [
        Build(c['group_id'], c['artifact_id'], c['version'],
              '/'.join(c['pom_path'].split('/')[:-1]), Build.SUCCESS, timestamp)
        for c in success_coordinates
    ]
    failure_modules = [
        Build(c['group_id'], c['artifact_id'], c['version'],
              '/'.join(c['pom_path'].split('/')[:-1]), Build.FAILURE, timestamp)
        for c in failure_coordinates
    ]
    return BuildState(__name__,
                      success_modules + failure_modules + previous_builds)


@log_params_return('debug')
def get_maven_infos(maven_repos):
    return [(r.status == Repo.STATUS_UPDATED, get_pom_info(f'{r.path}/pom.xml'))
            for r in maven_repos]


@log_params_return('debug')
def get_maven_repos(state):
    return [
        r for s in state if isinstance(s, SetupState) for r in s.repos
        if exists(f'{r.path}/pom.xml')
    ]


@log_params_return('debug')
def get_multi_modules(maven_infos, build_dir):
    multi_module_poms = []
    for modules_dir, filtered_maven_info in [
        ('super-pom-modules', [(mu, mi) for mu, mi in maven_infos
                               if 'packaging' in mi and mi['packaging'] == 'pom'
                               and 'super' in mi['artifact_id']]),
        ('pom-pom-modules', [(mu, mi) for mu, mi in maven_infos
                             if 'packaging' in mi and mi['packaging'] == 'pom'
                             and 'super' not in mi['artifact_id']]),
        ('other-modules', [(mu, mi) for mu, mi in maven_infos
                           if 'packaging' in mi and mi['packaging']
                           and mi['packaging'] not in ['jar', 'pom', 'war']]),
        ('jar-modules', [(mu, mi) for mu, mi in maven_infos
                         if 'packaging' not in mi or not mi['packaging']
                         or mi['packaging'] == 'jar']),
        ('war-modules', [(mu, mi) for mu, mi in maven_infos
                         if 'packaging' in mi and mi['packaging'] == 'war']),
    ]:
        updated = [mi for mu, mi in filtered_maven_info if mu]
        if filtered_maven_info and updated:
            # Create only if there are modules to build
            coordinates = [mi for mu, mi in filtered_maven_info]
            pom_dir = f'{build_dir}/{modules_dir}'
            pom_content = get_pom(coordinates, pom_dir, 'mm', modules_dir,
                                  '1.0.0-SNAPSHOT')
            multi_module_poms.append({
                'pom_dir': pom_dir,
                'pom_content': pom_content,
                'coordinates': coordinates,
                'updated': updated
            })
    return multi_module_poms


@log_params_return('debug')
def init(build_dir, repository_dir):
    makedirs(build_dir, exist_ok=True)
    if not exists(repository_dir):
        makedirs(repository_dir)
    return build_dir, repository_dir


@log_params_return('debug')
def get_not_built_paths(maven_infos, success_coordinates, failure_coordinates):
    builded_pom_paths = [
        c['pom_path'] for c in success_coordinates + failure_coordinates
    ]
    maven_pom_paths = [mi[1]['pom_path'] for mi in maven_infos]
    return [
        '/'.join(p.split('/')[:-1]) for p in maven_pom_paths
        if p not in builded_pom_paths
    ]


@log_params_return('debug')
def get_previous_builds(not_builded_paths, previous_state_file_path):

    print("#####")
    print(previous_state_file_path)
    print("#####")

    if previous_state_file_path:
        return [
            b for s in load(previous_state_file_path)
            if hasattr(s, 'step') and s.step == 'schmetterling.build.maven' for b in s.builds
            if b.path in not_builded_paths
        ]
    return []


# TODO Include latest commit and tags on that commit in build artifact
@log_params_return('info')
def execute(
        state,
        build_dir,
        repository_dir,
        settings_file,
        logback_file,
        timestamp,
):
    build_dir, repository_dir = init(build_dir, repository_dir)
    maven_repos = get_maven_repos(state)
    maven_infos = get_maven_infos(maven_repos)
    multi_modules = get_multi_modules(maven_infos, build_dir)
    create_multi_modules(multi_modules)
    success_coordinates, failure_coordinates = build_multi_modules(
        multi_modules,
        repository_dir,
        settings_file,
        logback_file,
    )
    previous_state_file_path = [s for s in state
                                if isinstance(s, StateState)][0].file_path
    not_built_paths = get_not_built_paths(
        maven_infos,
        success_coordinates,
        failure_coordinates,
    )
    previous_builds = get_previous_builds(
        not_built_paths,
        previous_state_file_path,
    )
    build_state = create_state(
        previous_builds,
        success_coordinates,
        failure_coordinates,
        timestamp,
    )
    return build_state
