import os
from subprocess import check_output, CalledProcessError, STDOUT

def system_call(command, cwd=None):
    """ 
    params:
        command: list of strings, ex. `["ls", "-l"]`
    returns: output, success
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

# output, success = system_call(["ls", "-l"])