WIFI_SSID = 'Guest_network'
WIFI_PASSWORD = 'RistoNOS8'
WEBHOOK_URL = 'https://maker.ifttt.com/trigger/Hens_door_changed/with/key/cvnTP3S5fA0NmpogPPldzq'
IFTTT_EVENT= 'Hens_door_changed'
LED_PIN = 2  # D4
LED2_PIN = 16  # D0
DEBUG_PIN = 14  # D5
DHT22_PIN = 4 #D2
TS_WEBHOOK_URL = 'https://api.thingspeak.com/update?api_key=FI944PH28TQ8YFJR&field1={temperature}&field2={humidity}'
LOG_INTERVAL = 3600
MOTOR_PIN= 5 #D1
MOTOR_DIR= 0 #D3
PWM_DUTY= 1200
DOOR_TIME= 45 #40
FILENAME= 'door_state.txt'
DAYLIGHT= ( (1, 92,     (-1.2/91, 7.2),     (1.5/91, 17)),
            (93, 134,   (0, 6),     (3.7/41, 18.5)),
            (135, 175,  (0, 6),     (0.9/40, 21.2)),
            (176, 216,  (0, 6),     (-1.0/40, 22.1)),
            (217, 258,  (0, 6),     (-2.0/41, 21.1)),
            (259, 337,  (2.3/78, 6),(-2.1/78, 19.1)),
            (338, 365,  (0, 8.3),   (0, 17)) )