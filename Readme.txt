2020-04-26 Mikael:
Tänker om för att spara batteriet. Nu gäller att koppla upp wifi en gång i veckan på söndag vid stängning. Då ges
spelregler för nästkommade vecka. Från uppvaknande gäller:
1. Kolla min status från fil på format [veckodag, open/closed]
2. Kör porten i motsats vad som lästes i 1.
3. Ändra status på filen
4. Läs mätvärden
5. Skriv till fil
6. Somna om enligt config-filen

På söndag vid stängning gäller:
1. Koppla upp mot wifi
2. Synca tiden
3. Kolla spänning
4. Skicka loggen via IFTT
5. stäng ner wifi
6. Somna om enlig config filen

Vid fel:
1. Koppla upp mot wifi
2. Skicka felmeddelande
3. Skicka senaste loggen
4. Stäng ner wifi

Lucka öppnas i 4 zoner
Vinter: 7:50-17:00 (33000, 53400)   [0]
Vår: 7:50-19:00 (40200,46200)       [1]
Sommar: 6:30-22:00 (55800,30600)    [2]
Höst: 7:50-19:00 (40200,46200)      [3]


Dagarna numreras Mån-Sön [0..6]

2020-01-26 Mikael:
start_motor.py tillsammans med config.py i motor_control var det som installerades i hönsluckeöppnaren.
Det är en omgjord version där fokus var på motorn och inte det andra. Nästa steg skulle
vara att kunna fånga fel och events via IFTT och mail. Sen skulle en enkel kamera kunna
visa tillståndet i hönshuset.
Nuvarande funktionalitet:
1. Öppna och stäng lucka på tid
2. Rapportera temp och fuktighet till Thingspeak

Tester
===========
import utime
import config
import main

time_now=(2020, 5, 14, 14, 54, 5, 1, 135)
s=main.adjusted_sleep(time_now, first_run=None)
assert(s==40200)
s=main.adjusted_sleep(time_now, first_run=True)
assert(s==14640)
f=open(config.FILENAME, 'r+')
a=f.read()
f.close()
assert(a in '1,Closed')

time_now=(2020, 12, 14, 14, 54, 5, 5, 135)
s=main.adjusted_sleep(time_now, first_run=True)
assert(s==7440)
s=main.adjusted_sleep(time_now, first_run=None)
assert(s==33000)
f=open(config.FILENAME, 'r+')
a=f.read()
f.close()
assert(a in '0,Closed')

lfp=open(config.LOGFILE, 'r+')
direction='Opened'
main.connect_wifi(lfp)
main.send_logfile(lfp)
s=main.sleep_until(lfp, direction, time_now, first_run=None)
assert (s==33000)
s=main.sleep_until(lfp, direction, time_now, first_run=True)
assert (s==7440)

f=open(config.FILENAME, 'r+')
f.seek(2,0)
f.write('Closed')
f.seek(0,0)
a=f.read()
f.close()
assert(a[2:] in 'Closed')

main.run()

tm=None
time_now=tm if tm else main.get_local_time()
assert (tm != time_now)
tm=(2020, 12, 14, 14, 54, 5, 5, 135)
time_now=tm if tm else main.get_local_time()
assert (tm == time_now)
main.run(tm)

f=open(config.FILENAME, 'r+')
f.seek(2,0)
f.write('Opened')
f.seek(0,0)
a=f.read()
f.close()
assert(a[2:] in 'Opened')
tm=(2020, 12, 14, 14, 54, 5, 6, 135)
main.run(tm)

lfp=open(config.LOGFILE, 'r+')
time_now=(2020, 6, 6, 14, 54, 5, 6, 135)
s=main.sleep_until(lfp, 'Opened', time_now, first_run=None)
f=open(config.FILENAME, 'r+')
a=f.read()
f.close()
assert (a in '1,Opened')
lfp.close()

Rename file
===========
lfp=open(config.LOGFILE, 'w')
lfp.close()
lfp=open(config.LOGFILE, 'r+')
lfp.write('first line\nsecond line\n')
main.rename_file(lfp)
assert (uos.stat('weekly_log.bak')[6] == 23)
assert (uos.stat('weekly_log.txt')[6] == 0)

send_logfile
==============
lfp=open(config.LOGFILE, 'r+')
main.connect_wifi(lfp)
main.send_logfile(lfp)
lfp.close()

log_me
=======
lfp=open(config.LOGFILE, 'r+')
a=main.log_me(lfp, "First line\nSecond line")
lfp.seek(0,0)
a=lfp.read()
lfp.close()
assert(a[-23:-1] in "First line\nSecond line")


connect_wifi
====
import network
lfp=open(config.LOGFILE, 'r+')
sta_if = network.WLAN(network.STA_IF)
a=sta_if.isconnected()
assert (a==False)
main.connect_wifi(lfp)
a=sta_if.isconnected()
assert (a==True)
main.disconnect_wifi(lfp)
a=sta_if.isconnected()
assert (a==False)
lfp.close()

pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
pin_dir= machine.Pin(config.MOTOR_DIR, machine.Pin.OUT) #Rotation direction
pwm_motor = machine.PWM(pin_motor)

pin_dir.on()
pwm_motor.duty(1200)
utime.sleep(51)
pwm_motor.duty(512)
utime.sleep(1)
pwm_motor.deinit()

pin_dir.off()
pwm_motor.duty(1200)
utime.sleep(43)
pwm_motor.duty(600)
utime.sleep(1)
pwm_motor.deinit()


Calculate sleep time
=====================
import config
lfp=open(config.LOGFILE, 'r+')
tm=(2020, 5, 24, 16, 55, 0, 4, 150)
a=main.calculate_sleep_time(lfp, 'Closed', tm)
assert (a==7320)

tm=(2020, 12, 4, 16, 55, 0, 6, 150)
a=main.calculate_sleep_time(lfp, 'Closed', tm)
assert (a==120)
lfp.close()

lfp=open(config.LOGFILE, 'r+')
tm=(2020, 12, 4, 17, 55, 0, 6, 150)
a=main.calculate_sleep_time(lfp, 'Closed', tm)
assert (a==56880)

tm=(2020, 12, 4, 8, 55, 0, 6, 150)
a=main.calculate_sleep_time(lfp, 'Opened', tm)
assert (a==28920)
lfp.close()