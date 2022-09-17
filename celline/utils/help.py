import sys


class Help:
    """
    Support help program
    """
    __HELP_PATH = f"{sys.path[0]}/docs/__help.txt"
    __HELP_CONTENT = ""

    @staticmethod
    def __get_help_content():
        if Help.__HELP_CONTENT == "":
            with open(Help.__HELP_PATH, mode="r") as f:
                Help.__HELP_CONTENT = "".join(f.readlines())
        return Help.__HELP_CONTENT

    @staticmethod
    def show():
        print(Help.__get_help_content())
