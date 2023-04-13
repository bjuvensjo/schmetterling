from schmetterling.analyze.state import Analyze, AnalyzeState


def test_analyze_state():
    analyze_state = AnalyzeState("step", "analyzes")

    assert analyze_state.step == "step"
    assert analyze_state.analyzes == "analyzes"

    assert (
        str(analyze_state) == "AnalyzeState: {'step': 'step', 'analyzes': 'analyzes'}"
    )

    assert analyze_state == AnalyzeState("step", "analyzes")


def test_analyze():
    analyze = Analyze("project", "name", "version", "path", "status", "timestamp")

    assert analyze.project == "project"
    assert analyze.name == "name"
    assert analyze.version == "version"
    assert analyze.path == "path"
    assert analyze.status == "status"
    assert analyze.timestamp == "timestamp"

    assert (
        str(analyze) == "Analyze: {'project': 'project', "
        "'name': 'name', "
        "'version': 'version', "
        "'path': 'path', "
        "'status': 'status', "
        "'timestamp': 'timestamp'}"
    )

    assert analyze == Analyze(
        "project", "name", "version", "path", "status", "timestamp"
    )
