import config
import ntptime
import network
import urequests
import utils
import utime

def set_time():
    ntptime.settime()

def connect_wifi(lfp):
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        utils.log_me(lfp, 'Connecting to WiFi...')
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        counter=0
        while not sta_if.isconnected():
            utime.sleep(1)
            counter+=1
            if counter > 14:
                raise RuntimeError('WLAN connection unavailable')
        utils.log_me(lfp,'Network config: {}'.format( sta_if.ifconfig()))

def disconnect_wifi(lfp):
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected():
        utils.log_me(lfp, 'Disconnecting from WiFi...')
        sta_if.active(False)

def send_logfile(lfp):
    utils.log_me(lfp, 'Invoking webhook in send_logfile')
    lfp.flush()
    lfp.seek(0,0) #Goto first of first line in file
    reason=lfp.read() #read all lines
    response = urequests.post(config.WEBHOOK_URL,
                              json={'value1': reason})
    if response is not None and response.status_code < 400:
        utils.log_me(lfp,'Webhook invoked',1)
        pass
    else:
        utils.log_me(lfp, 'Webhook failed',1)
        raise RuntimeError('Webhook failed')
