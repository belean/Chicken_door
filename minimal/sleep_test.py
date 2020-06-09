import machine
import utime
import config
import mynetwork
import chicken_door as cd
a=machine.reset_cause()
assert a==0, print('a is {}'.format(a))
a=cd.current_status(config.FILENAME, 'Closed')
assert a==('6', 'Closed'), print('a is {}'.format(a))
tm=(2020, 6, 9, 22, 13, 15, 1, 161)
lfp=open(config.LOGFILE, 'r+') #Open log file
mynetwork.connect_wifi(lfp)
mynetwork.set_time()
cd.run(tm)
