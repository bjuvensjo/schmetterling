from json import dumps
from json import loads

from jsonpickle import decode
from jsonpickle import encode

from schmetterling.core.log import log_params_return


@log_params_return('debug')
def to_json(obj, indent=0):
    if not obj:
        return ''
    json_string = encode(obj)
    return dumps(loads(json_string), indent=indent) if indent else json_string


@log_params_return('debug')
def from_json(json):
    if not json:
        return ''
    return decode(json)


@log_params_return('debug')
def dump(file_path, obj, indent=2):
    with open(file_path, 'wt', encoding='utf-8') as f:
        f.writelines(to_json(obj, indent))


@log_params_return('debug')
def load(file_path):
    with open(file_path, 'rt', encoding='utf-8') as f:
        return from_json(f.read())
