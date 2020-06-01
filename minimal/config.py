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
DOOR_TIME= 11 #51 #45 #40
FILENAME= 'door_state.txt'
LOGFILE= 'weekly_log.txt'
WEEK_DAYS= ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            #open, close
TIMINGS=  ( (7.8, 33000, 53400), #dec-feb
            (7.8, 40200, 46200), #mar-may
            (6.5, 55800, 30600), #jun-aug
            (7.8, 40200, 46200)) #sep-nov
            #Timings is (opening time, seconds open, seconds Closed)