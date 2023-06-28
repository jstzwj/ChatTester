


class MavenOutputParser(object):
    def __init__(self) -> None:
        pass

    def parse(self, output: str):
        lines = output.splitlines(keepends=True)