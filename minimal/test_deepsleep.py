import machine
import config
import chicken_door as main
"""
rtc=machine.RTC()
a=rtc.memory('7200')
a=rtc.memory()
assert a in b'7200', print('a in {}'.format(a))

main.deepsleep(10)

rtc=machine.RTC()
a=rtc.memory(str(int(rtc.memory())-3600))
a=rtc.memory()
assert a in b'3600', print('a in {}'.format(a))
"""
main.deepsleep(10)
