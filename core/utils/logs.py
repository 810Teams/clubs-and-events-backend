'''
    Core Application Displaying Log Functions
    core/utils/logs.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime


class Colors:
    ''' Colors class '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def colored(text, color):
    ''' Returns colorize text '''
    return color + text + Colors.ENDC


def _log(text, color=str()):
    ''' Display Django log base function '''
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

    now = datetime.now()
    formatted_datetime = '{:02d}/{}/{:04d} {:02d}:{:02d}:{:02d}'.format(
        now.day, months[now.month - 1], now.year, now.hour, now.minute, now.second
    )

    print(colored('[{}] {}'.format(formatted_datetime, text), color))


def log(text):
    ''' Display Django plain log '''
    _log(text)


def warning(text):
    ''' Display Django warning log '''
    _log(text, color=Colors.WARNING)


def error(text):
    ''' Display Django error log '''
    _log(text, color=Colors.FAIL)
