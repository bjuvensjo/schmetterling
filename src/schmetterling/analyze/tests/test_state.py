from schmetterling.analyze.state import Analyze, AnalyzeState


def test_analyze_state():
    analyze_state = AnalyzeState("step", "analyzes")

    assert "step" == analyze_state.step
    assert "analyzes" == analyze_state.analyzes

    assert "AnalyzeState: {'step': 'step', 'analyzes': 'analyzes'}" == str(
        analyze_state
    )

    assert AnalyzeState("step", "analyzes") == analyze_state


def test_analyze():
    analyze = Analyze("project", "name", "version", "path", "status", "timestamp")

    assert "project" == analyze.project
    assert "name" == analyze.name
    assert "version" == analyze.version
    assert "path" == analyze.path
    assert "status" == analyze.status
    assert "timestamp" == analyze.timestamp

    assert (
        "Analyze: {'project': 'project', "
        "'name': 'name', "
        "'version': 'version', "
        "'path': 'path', "
        "'status': 'status', "
        "'timestamp': 'timestamp'}" == str(analyze)
    )

    assert (
        Analyze("project", "name", "version", "path", "status", "timestamp") == analyze
    )
