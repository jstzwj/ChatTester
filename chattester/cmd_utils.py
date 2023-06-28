# Copyright 2023 by XiaHan. All rights reserved.
# This file is part of the ChatTester,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os
from subprocess import check_output, CalledProcessError, STDOUT

def system_call(command, cwd=None):
    """ 
    params:
        command: list of strings, ex. `["ls", "-l"]`
    returns: output, success
    usage: output, success = system_call(["ls", "-l"])
    """
    pwd = os.getcwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        output = check_output(command, stderr=STDOUT, shell=True).decode()
        success = True 
    except CalledProcessError as e:
        output = e.output.decode()
        success = False
    finally:
        os.chdir(pwd)
    return output, success
