from schmetterling.core.log import log_params_return


@log_params_return("info")
def execute(state):
    print("#" * 80)
    print("#" * 5, "bar")
    print("#" * 80)
