#!/usr/bin/env python3
import logging
import sys
from importlib import import_module
from traceback import print_exc

from schmetterling.core.log import log_params_return

log = logging.getLogger(__name__)


def get_execute(module=None, execute=None, **kwargs):
    return execute or import_module(module).execute


# TODO Manage state in its own git repo
@log_params_return("info")
def pipeline(steps):
    try:
        state = []
        for step in steps:
            execute = get_execute(**step)
            params = step.get("params", None)
            step_state = execute(state, **params) if params else execute(state)
            state.append(step_state)
        # log.info('State: %s', state)
        return state
    except Exception as e:
        print_exc(file=sys.stdout)
        log.error("Error in pipeline", e)
        # raise e
