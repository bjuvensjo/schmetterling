#!/usr/bin/env python3
from os import walk, rmdir
from shutil import rmtree

from schmetterling.core.log import log_params_return


@log_params_return('debug')
def rm_paths(dirs, root):
    for d in dirs:
        rmtree(d)

    # Remove empty directories
    for dir_path, dir_names, files in walk(root, topdown=False):
        if not dir_names and not files:
            rmdir(dir_path)

    return dirs
