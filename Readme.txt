2020-12-07 Mikael:
Skrev om och skapade micromal med en reducerad funktion. 
1. Koppla upp ESP8266 med microusb.
2. initiera rshell --port /dev/cu.SLAB_USBtoUART och resetta för att avbryta deep_sleep
3. controllera /pyboard/door_state.txt och machine.RTC().memory() De bör vara liknande
4. För att få den att somna om kör machine.reset() för en soft reset. Då initieas den och somnar

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
pyboard --device /dev/cu.SLAB_USBtoUART test.py


