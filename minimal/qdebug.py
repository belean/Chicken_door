import machine
import utime
import config
import chicken_door as cd
now=utime.localtime()
rc=machine.reset_cause()
status=cd.current_status(config.FILENAME)
rtc=machine.RTC()
mem= rtc.memory()
print('*** {} :: {} :: {} :: {} ***'.format(now, status, rc, mem))
with open(config.LOGFILE, 'r+') as fd:
    fd.seek(0,0)
    a=fd.read()
    print('*** weekly_log.txt ***',a)

with open('weekly_log.bak','r+') as fd:
    fd.seek(0,0)
    a=fd.read()
    print('*** weekly_log.bak ***',a)