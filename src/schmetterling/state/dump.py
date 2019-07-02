from schmetterling.core.log import log_params_return
from schmetterling.core.serialization import dump
from schmetterling.state.state import StateState


@log_params_return('info')
def execute(state, root, timestamp):
    file_path = f'{root}/{timestamp}-state.json'
    dump(file_path, state)
    return StateState(__name__, file_path)
