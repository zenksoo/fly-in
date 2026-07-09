class ProjectBaseException(Exception):
    def __init__(self, *args: object) -> None:
        self.msg = args[0]

    @classmethod
    def render_error(cls, msg):
        return f"Error Type '{cls.__name__}':\n\t{msg}"

    def __str__(self) -> str:
        return self.__class__.render_error(self.msg)


class MapParserError(ProjectBaseException):
    pass
