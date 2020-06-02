import chicken_door as main
import config
import utime
import sys

#Adjusted sleep
#=============
print('Open 1. Adjusted sleep!')
with open(config.FILENAME, 'w') as f:
    f.write('5,Closed')
try:
    lfp=open(config.LOGFILE, 'r+')
    time_now=(2020, 5, 14, 14, 54, 5, 1, 135)
    s=main.adjusted_sleep(lfp, time_now, 5, 'Opened')
    assert s==21960.0, print('s is {}'.format(s))
    s=main.adjusted_sleep(lfp, time_now, 5, 'Closed')
    assert s==59760.0, print('s is {}'.format(s))
    time_now=(2020, 5, 14, 6, 27, 5, 1, 135)
    s=main.adjusted_sleep(lfp, time_now, 5, 'Opened')
    assert s==52380.0, print('s is {}'.format(s))
    s=main.adjusted_sleep(lfp, time_now, 5, 'Closed')
    assert s==3780.0, print('s is {}'.format(s))
    time_now=(2020, 5, 14, 23, 5, 5, 1, 135)
    s=main.adjusted_sleep(lfp, time_now, 5, 'Opened')
    assert s==78900.0, print('s is {}'.format(s))
    s=main.adjusted_sleep(lfp, time_now, 5, 'Closed')
    assert s==30300.0, print('s is {}'.format(s))
    with open(config.FILENAME, 'r+') as f:
        a=f.read()
    assert a in '5,Closed', print('a is {}'.format(a))
    lfp.close()
except AssertionError as exc:
    sys.print_exception(exc)
print('1. Adjusted sleep OK!')

#calculate_sleep_time
#=====================
print('Open 2. calculate_sleep_time!')
with open(config.FILENAME, 'w') as f:
    f.write('12,Opened')
lfp=open(config.LOGFILE, 'r+')
# Normal run
time_now=(2020, 12, 14, 7, 36, 5, 5, 135)
s=main.calculate_sleep_time(lfp, 'Opened')
assert s==34200.0, print('s is {}'.format(s))
time_now=(2020, 12, 14, 17, 36, 5, 5, 135)
s=main.calculate_sleep_time(lfp, 'Closed')
assert s==52200.0, print('s is {}'.format(s))

#Resetted
time_now=(2020, 12, 14, 19, 54, 5, 5, 135)
s=main.calculate_sleep_time(lfp, 'Closed', time_now)
assert s==41760.0, print('s is {}'.format(s))
time_now=(2020, 12, 14, 14, 54, 5, 5, 135)
s=main.calculate_sleep_time(lfp, 'Opened', time_now)
assert s==7560.0, print('s is {}'.format(s))

with open(config.FILENAME, 'r+') as f:
    a=f.read()
    assert a in '12,Opened', print('a is {}'.format(a))
#
with open(config.FILENAME, 'w') as f:
    f.write('12,Closed')
time_now=(2020, 1, 5, 8, 54, 5, 6, 135)
s=main.calculate_sleep_time(lfp, 'Closed', time_now)
assert s==81360.0, print('s is {}'.format(s))
#
with open(config.FILENAME, 'r+') as f:
    a=f.read()
    assert a in '1,Closed', print('a is {}'.format(a))
#
lfp.close()
print('2. calculate_sleep_time OK!')
