from schmetterling.core.log import log_config, log_params_return
from schmetterling.log.state import LogState


@log_params_return('info')
def execute(state, log_dir, name, level):
    log_handlers = log_config(log_dir, name, level)
    return LogState(__name__, log_handlers['file_handler'].baseFilename)
