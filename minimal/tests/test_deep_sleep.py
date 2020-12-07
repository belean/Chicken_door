from chicken_door import deep_sleep, run_gate, schedule
import machine
import config
rtc=machine.RTC()
rtc.memory('312,17,19,Open')
state=['312','16','19','Open']
deep_sleep(state)
s=rtc.memory()
assert s.decode()=='312,18,19,Open', print('s is {}'.format(s))

deep_sleep(state)
s=rtc.memory()
assert s.decode()=='312,19,19,Open', print('s is {}'.format(s))

deep_sleep(7)
s=rtc.memory()
assert s.decode()=='312,19,7,Closed', print('s is {}'.format(s))

deep_sleep(state)
deep_sleep(state)
deep_sleep(state)
deep_sleep(state)
s=rtc.memory()
assert s.decode()=='312,23,7,Closed', print('s is {}'.format(s))

deep_sleep()
s=rtc.memory()
assert s.decode()=='313,0,7,Closed', print('s is {}'.format(s))

rtc.memory('365,23,7,Closed')
deep_sleep()
s=rtc.memory()
assert s.decode()=='1,0,7,Closed', print('s is {}'.format(s))

s=schedule(['312','16','19','Open'])
assert s==18.5, print('s is {}'.format(s))
s=schedule(['121','16','19','Open'])
assert s==21.5, print('s is {}'.format(s))
s=schedule(['365','16','19','Closed'])
assert s==7.5, print('s is {}'.format(s))
s=schedule(['120','16','19','Closed'])
assert s==7.5, print('s is {}'.format(s))
