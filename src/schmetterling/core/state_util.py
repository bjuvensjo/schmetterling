#!/usr/bin/env python3
from schmetterling.core.log import log_params_return


@log_params_return('debug')
def get_step_states(state, a_type=None, step=None):
    if a_type:
        return [s for s in state if isinstance(s, a_type)]
    if step:
        return [s for s in state if step == s.step]
    return state
