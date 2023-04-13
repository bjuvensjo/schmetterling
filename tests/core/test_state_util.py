#!/usr/bin/env python3
from schmetterling.build.state import BuildState
from schmetterling.core.state_util import get_step_states
from schmetterling.setup.state import SetupState


def test_get_step_states():
    state = [
        SetupState("schmetterling.setup.bitbucket", None),
        SetupState("schmetterling.setup.tfs", None),
        BuildState("schmetterling.build.maven", None),
    ]

    assert get_step_states(state) == [
        SetupState("schmetterling.setup.bitbucket", None),
        SetupState("schmetterling.setup.tfs", None),
        BuildState("schmetterling.build.maven", None),
    ]

    assert get_step_states(state, a_type=SetupState) == [
        SetupState("schmetterling.setup.bitbucket", None),
        SetupState("schmetterling.setup.tfs", None),
    ]

    assert get_step_states(state, step="schmetterling.setup.bitbucket") == [
        SetupState("schmetterling.setup.bitbucket", None),
    ]
