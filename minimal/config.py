# /Users/backis/Projects/micropython-tutorial/minimal/config.py
WIFI_SSID = 'Guest_network'
WIFI_PASSWORD = 'RistoNOS8'
WEBHOOK_URL = 'https://maker.ifttt.com/trigger/Hens_door_changed/with/key/cvnTP3S5fA0NmpogPPldzq'
IFTTT_EVENT= 'Hens_door_changed'
#LED_PIN = 2  # D4
#LED2_PIN = 16  # D0
DEBUG_PIN = 14  # D5
DHT22_PIN = 4 #D2
#TS_WEBHOOK_URL = 'https://api.thingspeak.com/update?api_key=FI944PH28TQ8YFJR&field1={temperature}&field2={humidity}'
#LOG_INTERVAL = 3600
MOTOR_PIN= 5 #D1
MOTOR_DIR= 0 #D3
PWM_DUTY= 1023
PWM_FREQ=50
DOOR_TIME= 55 #45 #40
FILENAME= 'door_state.txt'
LOGFILE= 'weekly_log.txt'
LOGLEVEL=0
DEEP_SLEEP= 3600
WEEK_DAYS= ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            #open, close

TIMINGS2= (
    ( 'jan', 0,  7, 18 ),
    ( 'feb', 31, 7, 18 ),
    ( 'mar', 59, 7, 19 ),
    ( 'apr', 90, 7,  20 ),
    ( 'maj', 120, 7, 21 ),
    ( 'jun', 151, 7, 23 ),
    ( 'jul', 181, 7, 23 ),
    ( 'aug', 212, 7, 21 ),
    ( 'sep', 243, 7, 20 ),
    ( 'okt', 273, 7, 19 ),
    ( 'nov', 304, 7, 18 ),
    ( 'dec', 334, 7, 18 ),
    ( 'dummy',365, 7, 18) )
    #Timings2 is (month, opening time, seconds open, closing time and seconds Closed)
