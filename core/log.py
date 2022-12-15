class Log:
    MAIN = '\033[38;5;50m'
    PLOAD = '\033[38;5;119m'
    GREEN = '\033[38;5;47m'
    BLUE = '\033[0;38;5;12m'
    ORANGE = '\033[0;38;5;214m'
    RED = '\033[1;31m'
    END = '\033[0m'
    BOLD = '\033[1m'

    INFO = f'{MAIN}Info{END}'
    WARN = f'{ORANGE}Warning{END}'
    IMPORTANT = WARN = f'{ORANGE}Important{END}'
    FAILED = f'{RED}Fail{END}'
    DEBUG = f'{ORANGE}Debug{END}'

    verbose = False

    def __init__(self, verbose):
        self.verbose = verbose

    def message(self, msg):
        print(f"{msg}")

    def info(self, msg):
        print(f"[{self.INFO}] {msg}")

    def warn(self, msg):
        print(f"[{self.WARN}] {msg}")

    def important(self, msg):
        print(f"[{self.IMPORTANT}] {msg}")

    def failed(self, msg):
        print(f"[{self.FAILED}] {msg}")

    def debug(self, msg):
        if self.verbose:
            print(f"[{self.DEBUG}] {msg}")

    def payload(self, msg):
        print(f"{self.GREEN}{msg}{self.END}")