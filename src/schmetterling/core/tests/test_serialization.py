#!/usr/bin/env python3

from schmetterling.build_status.state import BuildStatusState
from schmetterling.build_status.state import Repo
from schmetterling.core.serialization import from_json
from schmetterling.core.serialization import to_json

d = {'a': [1, 2, 3]}
state = [BuildStatusState('step', [Repo('project',
                                          'name' + str(n),
                                          'path' + str(n),
                                          'commit_id' + str(n),
                                          'build_url',
                                          'status') for n in range(5)])]

d_json = '{"a": [1, 2, 3]}'
d_json_formatted = '''{
  "a": [
    1,
    2,
    3
  ]
}'''

state_json = '[{"py/object": "schmetterling.build_status.state.BuildStatusState", "repos": [' \
             '{"py/object": "schmetterling.build_status.state.Repo", "build_url": "build_url", "commit_id": "commit_id0", ' \
             '"name": "name0", "path": "path0", "project": "project", "status": "status"}, ' \
             '{"py/object": "schmetterling.build_status.state.Repo", "build_url": "build_url", "commit_id": "commit_id1", ' \
             '"name": "name1", "path": "path1", "project": "project", "status": "status"}, ' \
             '{"py/object": "schmetterling.build_status.state.Repo", "build_url": "build_url", "commit_id": "commit_id2", ' \
             '"name": "name2", "path": "path2", "project": "project", "status": "status"}, ' \
             '{"py/object": "schmetterling.build_status.state.Repo", "build_url": "build_url", "commit_id": "commit_id3", ' \
             '"name": "name3", "path": "path3", "project": "project", "status": "status"}, ' \
             '{"py/object": "schmetterling.build_status.state.Repo", "build_url": "build_url", "commit_id": "commit_id4", ' \
             '"name": "name4", "path": "path4", "project": "project", "status": "status"}], "step": "step"}]'
state_json_formatted = '''[
  {
    "py/object": "schmetterling.build_status.state.BuildStatusState",
    "repos": [
      {
        "py/object": "schmetterling.build_status.state.Repo",
        "build_url": "build_url",
        "commit_id": "commit_id0",
        "name": "name0",
        "path": "path0",
        "project": "project",
        "status": "status"
      },
      {
        "py/object": "schmetterling.build_status.state.Repo",
        "build_url": "build_url",
        "commit_id": "commit_id1",
        "name": "name1",
        "path": "path1",
        "project": "project",
        "status": "status"
      },
      {
        "py/object": "schmetterling.build_status.state.Repo",
        "build_url": "build_url",
        "commit_id": "commit_id2",
        "name": "name2",
        "path": "path2",
        "project": "project",
        "status": "status"
      },
      {
        "py/object": "schmetterling.build_status.state.Repo",
        "build_url": "build_url",
        "commit_id": "commit_id3",
        "name": "name3",
        "path": "path3",
        "project": "project",
        "status": "status"
      },
      {
        "py/object": "schmetterling.build_status.state.Repo",
        "build_url": "build_url",
        "commit_id": "commit_id4",
        "name": "name4",
        "path": "path4",
        "project": "project",
        "status": "status"
      }
    ],
    "step": "step"
  }
]'''


def test_to_json():
    assert '' == to_json(None)
    assert '' == to_json('')
    assert '' == to_json([])
    assert '' == to_json({})

    assert d_json == to_json(d)
    assert d_json_formatted == to_json(d, 2)

    assert state_json == to_json(state)
    assert state_json_formatted == to_json(state, 2)


def test_from_json():
    assert '' == from_json(None)
    assert '' == from_json('')

    assert d == from_json(d_json)
    assert d == from_json(d_json_formatted)

    assert state == from_json(state_json)
    assert state == from_json(state_json_formatted)
