from schmetterling.core.log import log_params_return


@log_params_return("info")
def execute(state, param1, param2):
    print("#" * 80)
    print("#" * 5, "foo", param1, param2)
    print("#" * 80)
