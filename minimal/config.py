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
LOGLEVEL=1
WEEK_DAYS= ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            #open, close
TIMINGS=  ( (7.8, 33000, 53400), #dec-feb
            (7.8, 40200, 46200), #mar-may
            (6.5, 55800, 30600), #jun-aug
            (7.8, 40200, 46200)) #sep-nov
            #Timings is (opening time, seconds open, seconds Closed)

TIMINGS2= ( ('dummy', 0, 0.0, 0, 86400.0),
    ( 'jan', 7.5, 34200.0, 17.0, 52200.0 ),
    ( 'feb', 7.5, 36000.0, 17.5, 50400.0 ),
    ( 'mar', 7.5, 37800.0, 18.0, 48600.0 ),
    ( 'apr', 7.5, 41400.0, 19.0, 45000.0 ),
    ( 'maj', 7.5, 48600.0, 21.0, 37800.0 ),
    ( 'jun', 7.5, 48600.0, 21.0, 37800.0 ),
    ( 'jul', 7.5, 52200.0, 22.0, 34200.0 ),
    ( 'aug', 7.5, 48600.0, 21.0, 37800.0 ),
    ( 'sep', 7.5, 41400.0, 19.0, 45000.0 ),
    ( 'okt', 7.5, 37800.0, 18.0, 48600.0 ),
    ( 'nov', 7.5, 36000.0, 17.5, 50400.0 ),
    ( 'dec', 7.5, 34200.0, 17.0, 52200.0 ) )
    #Timings2 is (month, opening time, seconds open, closing time and seconds Closed)
