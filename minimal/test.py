import chicken_door as main
import config
import utime

lfp=open(config.LOGFILE, 'r+')
time_now=(2020, 5, 4, 14, 54, 5, 6, 135)
status=main.current_status(config.FILENAME,'Closed')
s=main.calculate_sleep_time(lfp, 'Closed', time_now)
assert s==59760.0, print('s is {}'.format(s))
assert status[1]=='Closed', print('status is {}'.format(status))

print("Open current_status!")
main.current_status(config.FILENAME)
with open(config.FILENAME, 'r+') as f:
    f.seek(0,0)
    a=f.read()
    assert a in '5,Closed', print('a is {}'.format(a))

main.current_status(config.FILENAME, 'Opened')
with open(config.FILENAME, 'r+') as f:
    f.seek(0,0)
    a=f.read()
    assert a in '5,Opened', print('a is {}'.format(a))

main.current_status(config.FILENAME, None, 5)
with open(config.FILENAME, 'r+') as f:
    f.seek(0,0)
    a=f.read()
    assert a in '5,Opened', print('a is {}'.format(a))

main.current_status(config.FILENAME, 'Closed', 12)
with open(config.FILENAME, 'r+') as f:
    f.seek(0,0)
    a=f.read()
    assert a in '12,Closed', print('a is {}'.format(a))

print("Open current_status OK!")


#Rename file
#===========

import uos
print("open rename file!")
lfpw=open(config.LOGFILE, 'w')
lfpw.close()

with open(config.LOGFILE, 'r+') as lfp:
    lfp.write('first line\nsecond line\n')
    main.rename_file(lfp)
    a=uos.stat('weekly_log.bak')[6] - uos.stat('weekly_log.txt')[6]
    assert a == 23, print('a is {}'.format(a))


with open(config.LOGFILE, 'r+') as lfp:
    main.log_me(lfp, "First line\nSecond line")
    lfp.seek(0,0)
    a=lfp.read()
    assert a[-23:-1] in "First line\nSecond line", print('a is {}'.format(a))



print("machine!")
lfp=open(config.LOGFILE, 'r+')
main.run_gate(lfp, 'Closed')
utime.sleep(1)
main.run_gate(lfp, 'Opened')
lfp.close()
