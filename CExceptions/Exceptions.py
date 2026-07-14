import re


class ProjectBaseException(Exception):
    def __init__(self, *args: object) -> None:
        self.msg: str = str(args[0])

    def __str__(self) -> str:
        return re.sub(r"( +)", " ", self.msg)


class MapParserError(ProjectBaseException):
    pass
