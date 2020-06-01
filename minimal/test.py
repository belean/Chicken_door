import chicken_door as main
import config
import utime

#Adjusted sleep
#=============
print('Open 1. Adjusted sleep!')
f=open(config.FILENAME, 'w')
f.write('5,Closed')
f.close()
lfp=open(config.LOGFILE, 'r+')
time_now=(2020, 5, 14, 14, 54, 5, 1, 135)
s=main.adjusted_sleep(lfp, time_now, 5)
assert(s==21760.0)
with open(config.FILENAME, 'r+') as f:
    a=f.read()
assert(a in '5,Closed')
lfp.close()
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
#print(s)
assert(s==34200.0)
time_now=(2020, 12, 14, 17, 36, 5, 5, 135)
s=main.calculate_sleep_time(lfp, 'Closed')
#print(s)
assert(s==52200.0)

#Resetted
time_now=(2020, 12, 14, 19, 54, 5, 5, 135)
s=main.calculate_sleep_time(lfp, 'Closed', time_now)
assert(s==41640.0)
time_now=(2020, 12, 14, 14, 54, 5, 5, 135)
s=main.calculate_sleep_time(lfp, 'Opened', time_now)
assert(s==7424.0)

with open(config.FILENAME, 'r+') as f:
    a=f.read()
    assert(a in '12,Opened')
#
with open(config.FILENAME, 'w') as f:
    f.write('12,Closed')
time_now=(2020, 1, 5, 8, 54, 5, 6, 135)
s=main.calculate_sleep_time(lfp, 'Closed', time_now)
#print(s)
assert(s==28992.0)
#
with open(config.FILENAME, 'r+') as f:
    a=f.read()
    print(a)
    assert(a in '1,Closed')
#
lfp.close()
print('2. calculate_sleep_time OK!')

print("Open current_status!")
main.current_status(config.FILENAME)
with open(config.FILENAME, 'r+') as f:
    f.seek(0,0)
    a=f.read()
    print(a)
    assert( a in '1,Closed')

main.current_status(config.FILENAME, 'Opened')
with open(config.FILENAME, 'r+') as f:
    f.seek(0,0)
    a=f.read()
    assert( a in '1,Opened')

main.current_status(config.FILENAME, None, 5)
with open(config.FILENAME, 'r+') as f:
    f.seek(0,0)
    a=f.read()
    assert( a in '5,Opened')

main.current_status(config.FILENAME, 'Closed', 12)
with open(config.FILENAME, 'r+') as f:
    f.seek(0,0)
    a=f.read()
    assert( a in '12,Closed')

print("Open current_status OK!")


#Rename file
#===========
"""
import uos
print("open rename file!")
with open(config.LOGFILE, 'w') as lfp:
    pass

with open(config.LOGFILE, 'r+') as lfp:
    lfp.write('first line\nsecond line\n')
    main.rename_file(lfp)
    a=uos.stat('weekly_log.bak')[6] - uos.stat('weekly_log.txt')[6]
    print("a: "+str(a))
    assert (a == 24)
"""

with open(config.LOGFILE, 'r+') as lfp:
    main.log_me(lfp, "First line\nSecond line")
    lfp.seek(0,0)
    a=lfp.read()
    assert(a[-23:-1] in "First line\nSecond line")



print("machine!")
lfp=open(config.LOGFILE, 'r+')
main.run_gate(lfp, 'Closed')
utime.sleep(1)
main.run_gate(lfp, 'Opened')
lfp.close()
