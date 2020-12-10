class Config:
    def __init__(self):
        self.WIFI_SSID = 'Guest_network'
        self.WIFI_PASSWORD = 'RistoNOS8'
        self.DEBUG_PIN = 14  # D5
        self.MOTOR_PIN = 5  # D1
        self.MOTOR_DIR = 0  # D3
        self.PWM_DUTY = 1023
        self.PWM_FREQ = 50
        self.DOOR_TIME = 50  # 45 #40
        self.FILENAME = 'door_state.txt'
        self.DEEP_SLEEP = 3600
        self.TIMINGS2 = (7, 19)  # open, close
        self.LOGFILE = 'cd_log.txt'
        self.LOGLEVEL = 0
