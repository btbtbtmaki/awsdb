# constants

COLOR_ENDC    = '\033[0m'
COLOR_BOLD    = '\033[1m'
COLOR_BLACK   = '\033[90m'
COLOR_RED     = '\033[91m'
COLOR_GREEN   = '\033[92m'
COLOR_YELLOW  = '\033[93m'
COLOR_BLUE    = '\033[94m'
COLOR_MAGENTA = '\033[95m'
COLOR_CYAN    = '\033[96m'
COLOR_WHITE   = '\033[97m'
COLOR_DEFAULT = '\033[99m'

FRONT_END     ='[FRONT END] - '
BACK_END      ='[BACK END] - '
WARNING       ='[WARNING] - '
FAIL          ='[FAIL] - '

def log_front(msg):
    print COLOR_CYAN + FRONT_END + msg + COLOR_ENDC

def log_back(msg):
    print COLOR_GREEN + BACK_END + msg + COLOR_ENDC

def log_warning(msg):
    print COLOR_YELLOW + BACK_END + msg + COLOR_ENDC

def log_fail(msg):
    print COLOR_RED + BACK_END + msg + COLOR_ENDC

def log_status(msg):
    print COLOR_BLUE + BACK_END + msg + COLOR_ENDC
