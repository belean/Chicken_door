from config import Config
import ntptime
import network
import utime
from utils import Logger

config = Config()
log = Logger()


def set_time():
    log.log_me("  Entering set_time()!")
    success = False
    count = 0
    while not success:
        try:
            count += 1
            ntptime.settime()
            success = True
        except Exception as exc:
            log.log_me("   Exception: {}".format(exc), 3)
            if count > 12:
                raise RuntimeError('ntptime unavailable')
            utime.sleep(5)


def connect_wifi():
    log.log_me("  Entering connect_wifi()!")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        log.log_me('  Connecting to WiFi...')
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        counter = 0
        while not sta_if.isconnected():
            utime.sleep(1)
            counter += 1
            if counter > 14:
                log.log_me("  WLAN connection unavailable", 5)
                raise RuntimeError('WLAN connection unavailable')


def disconnect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected():
        log.log_me('  Disconnecting from WiFi...')
        sta_if.active(False)
