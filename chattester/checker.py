# Copyright 2023 by XiaHan. All rights reserved.
# This file is part of the ChatTester,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


from chattester.cmd_utils import system_call
import shutil
import os

class UnitTestChecker(object):
    def __init__(self, project_path: str) -> None:
        self.project_path = project_path
    
    def get_core_class_name(self, path: str) -> str:
        file_path = os.path.normpath(path).replace("\\", "/")
        core_class_name = file_path.split("/")[-1].replace(".java", "")
        return core_class_name
    
    def create_test(self, path: str, content: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def remove_test(self, path: str):
        os.remove(path)

    def run_tests(self):
        output, success = system_call(["mvn", "clean", "verify"], cwd=self.project_path)
        return output, success