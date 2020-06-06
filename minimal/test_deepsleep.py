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
rtc=machine.RTC()
a=rtc.memory('7200')
a=main.deepsleep_util(10)
assert a==10, print('a is {}'.format(a))
b=rtc.memory()
assert b in b'7200', print('b is {}'.format(b))

a=main.deepsleep_util()
assert a==3600, print('a is {}'.format(a))
b=rtc.memory()
assert b in b'3600', print('b is {}'.format(b))

a=main.deepsleep_util(3600)
assert a==3600, print('a is {}'.format(a))

a=main.deepsleep_util(3599)
assert a==3599, print('a is {}'.format(a))


a=main.deepsleep_util(3601)
assert a==3600, print('a is {}'.format(a))
b=rtc.memory()
assert b in b'3601', print('b is {}'.format(b))
a=main.deepsleep_util(7300)
assert a==3600, print('a is {}'.format(a))
b=rtc.memory()
assert b in b'7300', print('b is {}'.format(b))

a=main.deepsleep_util()
assert a==3600, print('a is {}'.format(a))
b=rtc.memory()
assert b in b'3700', print('b is {}'.format(b))