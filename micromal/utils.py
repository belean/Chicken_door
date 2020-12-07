from config import Config
import utime
import machine
import os

config = Config()


class Logger(object):
    log = list()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Logger, cls).__new__(cls)
        return cls.instance

    def log_me(self, message, log=0):
        tm = get_local_time()
        tm_str = '-'.join(map(str, tm[0:3]))+'T'+':'.join(map(str, tm[3:6]))
        if is_debug():
            print('@{}: {}'.format(tm_str, message))
        if log >= config.LOGLEVEL:
            self.log.append('@{}: {}'.format(tm_str, message))

    def write_to_log(self):
        self.log_me("  Writing log\n")
        lfp = open(config.LOGFILE, 'a')  # Erase file
        lfp.write('\n'.join(self.log))
        lfp.close()

    def rotate_log(self):
        """ Rotate log to free space on device """
        s_fs = os.statvfs('//')
        free_space = s_fs[0]*s_fs[3]

        log_file_size = os.stat(config.LOGFILE)[6]
        if log_file_size > free_space//2:  # bigger than half of free space
            fr = open(config.LOGFILE, 'r')
            fr.seek(log_file_size//2, 0)
            tmp = fr.read()
            fr.close()

            fw = open(config.LOGFILE, 'w')
            fw.write(tmp)
            fw.close()


log = Logger()


def get_local_time():
    """ Adjust the time to avoid drift """
    # log.log_me("  Entering get_local_time()!")
    tm = utime.localtime()  # In UTC
    add_hour = 1
    if((tm[1] > 3 and tm[1] < 10) or ((31-tm[2]) <= 6 and (tm[6] < 6-(31-tm[2])
       or tm[6] == 6))):  # Summer time
        add_hour = 2
    ltime = utime.mktime((tm[0], tm[1], tm[2], tm[3]+add_hour, tm[4], tm[5],
                          tm[6], tm[7]))  # Adds one/two hour from UTC
    return utime.localtime(ltime)


def is_debug():
    debug = machine.Pin(config.DEBUG_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    if debug.value() == 0:
        # log.log_me('  Debug mode detected.')
        return True
    return False


def sync_file():
    """Syncronizes files from rtc and filesystem. Since rtc erases after
    no battery we use the saved filesystem values"""
    # state=['312','16','19','Open']
    log.log_me("  Entering sync_file()!")
    state = list()  # init
    tm = get_local_time()  # get current time
    with open(config.FILENAME, 'r') as f:
        f.seek(0, 0)
        state = f.read().strip().split(',')
    state[0] = str(tm[7])  # Update day
    state[1] = str(tm[3])  # and hour

    # write to rtc memory
    rtc = machine.RTC()
    rtc.memory(','.join(state))

    # write to file
    with open(config.FILENAME, 'w') as fw:
        fw.seek(0, 0)
        fw.write(','.join(state))
    return state


def get_reset_code():
    return {
        0: "PWRON_RESET",
        1: "WDT_RESET",
        4: "SOFT_RESET",
        5: "DEEPSLEEP_RESET",
        6: "HARD_RESET"
    }
