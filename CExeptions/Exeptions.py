class ProjectBaseException(Exception):
    def __init__(self, *args: object) -> None:
        self.msg = args[0]

    def render_error(self):
        return f"Error Type '{self.__class__.__name__}':\n\t{self.msg}"

    def __str__(self) -> str:
        return self.msg


class MapParserError(ProjectBaseException):
    pass
