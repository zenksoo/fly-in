import re


class CodeBaseException(Exception):
    """
    Base exception class for the project. Provides a custom string
    representation that includes the exception type and traceback
    information.
    """
    def __init__(self, *args: object) -> None:
        """
        Initialize the exception with a message and optional
        traceback information.
        """
        super().__init__(*args)

    def __str__(self) -> str:
        """
        Return a string representation of the exception, including
        the exception type and traceback information.
        """

        print(f"\033[41m\033[37m  {self.__class__.__name__}  \033[49m")
        print(f"\t{super().__str__()}")

        tb = self.__traceback__
        # walk to the last frame — where the raise actually happened
        while tb and tb.tb_next:
            if not tb.tb_next:
                break
            tb = tb.tb_next

        if tb:
            filename = tb.tb_frame.f_code.co_filename
            lineno = tb.tb_lineno
            func_name = tb.tb_frame.f_code.co_name
            print(f"\n- Error In {func_name}()")
            print(f"- Error Line : {filename}:{lineno} ")
        return ""


class ProjectBaseException(Exception):
    """
    Base exception class for the project. Provides a custom string
    representation that includes the exception type and traceback
    information.
    """

    def __init__(self, *args: object) -> None:
        """
        Initialize the exception with a message and optional
        traceback information.
        """
        self.msg: str = str(args[0])

    def __str__(self) -> str:
        """
        Return a string representation of the exception, including the
        exception type and traceback information. """
        # print("\033[H\033[J")
        error_type = f"\033[41m {self.__class__.__name__} \033[49m"
        return f"{error_type}: {re.sub(r"( +)", " ", self.msg)}"


class MapParserError(ProjectBaseException):
    """ Exception raised when there is an error parsing a map file. """

    pass


class MetaDataParserError(ProjectBaseException):
    """ Exception raised when there is an error parsing metadata. """
    pass


class CanvasError(ProjectBaseException):
    """ Exception raised when there is an error related to the canvas. """
    pass


class InvalidMap(ProjectBaseException):
    """ Exception raised when the map is invalid. """
    pass


class InvalidCliArgument(ProjectBaseException):
    """ Exception raised when a command line argument is invalid. """
    pass


class InvalidArgument(CodeBaseException):
    """ Exception raised when an argument is invalid. """
    pass
