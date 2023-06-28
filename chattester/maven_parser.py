# Copyright 2023 by XiaHan. All rights reserved.
# This file is part of the ChatTester,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


from typing import List, Optional, Tuple
import re

FILE_PATTERN = r"(/[a-zA-Z\./:]*[\s]?):\[([0-9]+),([0-9]+)\]"

class MavenOutputLine(object):
    def __init__(self, level: str, msg: str) -> None:
        self.level = level
        self.msg = msg
    
    def __str__(self) -> str:
        return f"{self.level}: {self.msg}"
    
    def get_path(self) -> Optional[str]:
        match = re.search(FILE_PATTERN, self.msg)

        if match:
            return match.group(1)
        else:
            return None
    
    def get_line_col(self) -> Optional[Tuple[int, int]]:
        match = re.search(FILE_PATTERN, self.msg)

        if match:
            return int(match.group(2)), int(match.group(3))
        else:
            return None
    
    def get_message(self) -> Optional[str]:
        path = self.get_path()
        if path is None:
            return self.msg
        else:
            return re.sub(FILE_PATTERN, '', self.msg)

class MavenOutput(object):
    def __init__(self, output: List[MavenOutputLine] = []) -> None:
        self.output: List[MavenOutputLine] = output
        self.status: Optional[str] = None
        self.text: str = ''
    
    def __len__(self) -> int:
        return len(self.output)

    def append(self, value):
        self.output.append(value)
    
    def __setitem__(self, key, value):
        self.output[key] = value

    def __getitem__(self, key):
        return self.output[key]

    def filter(self, level: str) -> "MavenOutput":
        return MavenOutput([line for line in self.output if line.level == level])

class MavenOutputParser(object):
    def __init__(self) -> None:
        pass

    def parse(self, output: str):
        lines = output.splitlines(keepends=True)

        out = MavenOutput()
        out.text = output
        for i, line in enumerate(lines):
            if line.startswith("[INFO]"):
                out.append(MavenOutputLine("info", line[6:].strip()))
            elif line.startswith("[WARNING]"):
                out.append(MavenOutputLine("warning", line[9:].strip()))
            elif line.startswith("[ERROR]"):
                out.append(MavenOutputLine("error", line[7:].strip()))
            else:
                out[-1].msg += "\n" + line.strip()
            
            if "BUILD FAILURE" in line:
                out.status = "failure"
                break
            elif "BUILD SUCCESS" in line:
                out.status = "success"
                break
        
        return out