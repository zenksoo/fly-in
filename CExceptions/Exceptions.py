import re


class CodeBaseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:

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
    def __init__(self, *args: object) -> None:
        self.msg: str = str(args[0])

    def __str__(self) -> str:
        return re.sub(r"( +)", " ", self.msg)


class MapParserError(ProjectBaseException):
    pass


class MetaDataParserError(ProjectBaseException):
    pass


class CanvasError(ProjectBaseException):
    pass


class InvalidArgument(CodeBaseException):
    pass
