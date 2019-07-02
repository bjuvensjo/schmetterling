from unittest.mock import call, patch

from schmetterling.analyze.sonarqube import analyze, get_already_analyzed, get_not_analyzed_builds, init
from schmetterling.analyze.sonarqube import analyze_all
from schmetterling.analyze.sonarqube import create_state
from schmetterling.analyze.sonarqube import get_success_builds
from schmetterling.analyze.state import Analyze, AnalyzeState
from schmetterling.build.state import Build, BuildState


def test_analyze():
    with patch('schmetterling.analyze.sonarqube.run_command', return_value=0):
        build = Build(
            name='name',
            path='path',
            project='project',
            version='version',
            status='status',
            timestamp='timestamp',
        )
        assert (0, 'log_dir/name.log', build) == analyze(
            'log_dir',
            'settings_file',
            'sonar_plugin',
            'sonar_url',
            'sonar_auth_token',
            build,
        )


def test_analyze_all():
    assert list(range(1, 11)) == analyze_all(lambda x: x + 1, range(10))


def test_create_state():
    build = Build(
        name='name',
        path='path',
        project='project',
        version='version',
        status='status',
        timestamp='timestamp',
    )
    sonar_analyzes = [(0, 'log_dir/name-sonar.log', build)]
    assert AnalyzeState('schmetterling.analyze.sonarqube', [
        Analyze(
            **{
                'project': 'project',
                'name': 'name',
                'version': 'version',
                'path': 'path',
                'status': 'SUCCESS',
                'timestamp': 'timestamp'
            })
    ]) == create_state(sonar_analyzes, [])


def test_get_success_builds():
    success_builds = [
        Build(
            project='project',
            name='name1',
            version='1.0.0-SNAPSHOT',
            path='path1',
            status=Build.SUCCESS,
            timestamp='20181102T111722.293830',
        )
    ]
    failure_builds = [
        Build(
            project='project',
            name='name1',
            version='1.0.0-SNAPSHOT',
            path='path1',
            status=Build.FAILURE,
            timestamp='20181102T111722.293830',
        )
    ]

    assert [] == get_success_builds([
        BuildState('schmetterling.build.not_maven', success_builds + failure_builds)
    ])

    assert success_builds == get_success_builds(
        [BuildState('schmetterling.build.maven', success_builds + failure_builds)])


def test_init():
    with patch('schmetterling.analyze.sonarqube.makedirs') as mock_makedirs:
        with patch('schmetterling.analyze.sonarqube.exists', return_value=True) as mock_exists:
            assert 'log_dir' == init('log_dir')
            assert [call('log_dir')] == mock_exists.mock_calls
            assert [] == mock_makedirs.mock_calls
        with patch('schmetterling.analyze.sonarqube.exists', return_value=False) as mock_exists:
            assert 'log_dir' == init('log_dir')
            assert [call('log_dir')] == mock_exists.mock_calls
            assert [call('log_dir')] == mock_makedirs.mock_calls


def test_get_already_analyzed():
    success_builds = [Build(None, None, None, 'p1', None, 'timestamp_current'),
                      Build(None, None, None, 'p2', None, 'timestamp_current'),
                      Build(None, None, None, 'p3', None, 'timestamp_current')]
    p1 = Analyze(None, None, None, 'p1', Analyze.SUCCESS, 'timestamp_current')
    p2 = Analyze(None, None, None, 'p2', Analyze.SUCCESS, 'timestamp_not_current')
    p3 = Analyze(None, None, None, 'p3', Analyze.FAILURE, 'timestamp_current')
    p4 = Analyze(None, None, None, 'p4', Analyze.SUCCESS, 'timestamp_current')
    analyzes = (p1, p2, p3, p4)
    previous_state = (AnalyzeState('schmetterling.analyze.sonarqube', analyzes),
                      AnalyzeState('schmetterling.analyze.not_sonarqube', analyzes))
    with patch('schmetterling.analyze.sonarqube.load', return_value=previous_state):
        assert [p1] == get_already_analyzed(success_builds, 'previous_state_file')


def test_get_not_analyzed_builds():
    p1 = Build(None, None, None, 'p1', None, 'timestamp_current')
    success_builds = [p1,
                      Build(None, None, None, 'p2', None, 'timestamp_current'),
                      Build(None, None, None, 'p3', None, 'timestamp_current')]
    already_analyzed = [
        Analyze(None, None, None, 'p2', Analyze.SUCCESS, 'timestamp_current'),
        Analyze(None, None, None, 'p3', Analyze.FAILURE, 'timestamp_current'),
        Analyze(None, None, None, 'p4', Analyze.SUCCESS, 'timestamp_current')]
    assert [p1] == get_not_analyzed_builds(success_builds, already_analyzed)
