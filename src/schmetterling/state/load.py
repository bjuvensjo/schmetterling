from glob import glob
from os.path import realpath
from pathlib import Path

from schmetterling.core.log import log_params_return
from schmetterling.state.state import StateState


@log_params_return('debug')
def get_state_files(root, sort=True):
    state_files = [
        Path(realpath(p))
        for p in glob(f'{root}/**/*-state.json', recursive=True)
    ]
    return sorted(state_files, key=lambda f: f.name) if sort else state_files


@log_params_return('info')
def execute(state, root):
    state_files = get_state_files(root)
    if state_files:
        file_path = state_files[-1]  # latest
        return StateState(__name__, file_path.as_posix())
    else:
        return StateState(__name__, None)
