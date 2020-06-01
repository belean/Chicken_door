import machine
import utime
import config
import urequests
import network
import dht
import ntptime

def connect_wifi():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to WiFi...')
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not sta_if.isconnected():
            utime.sleep(1)
    print('Network config:', sta_if.ifconfig())

def call_webhook(reason):
    print('Invoking webhook')
    response = urequests.post(config.WEBHOOK_URL,
                              json={'value1': reason})
    if response is not None and response.status_code < 400:
        print('Webhook invoked')
    else:
        print('Webhook failed')
        raise RuntimeError('Webhook failed')

def show_error():
    led = machine.Pin(config.LED_PIN, machine.Pin.OUT)
    for i in range(3):
        led.on()
        utime.sleep(0.5)
        led.off()
        utime.sleep(0.5)
    led.on()

def is_debug():
    debug = machine.Pin(config.DEBUG_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    if debug.value() == 0:
        print('Debug mode detected.')
        return True
    return False

def get_temperature_and_humidity():
    dht22 = dht.DHT22(machine.Pin(config.DHT22_PIN))
    dht22.measure()
    temperature = dht22.temperature()
    return temperature, dht22.humidity()

def log_data(temperature, humidity):
    print('Invoking log webhook')
    url = config.TS_WEBHOOK_URL.format(temperature=temperature,
                                    humidity=humidity)
    response = urequests.get(url)
    if response.status_code < 400:
        print('Webhook invoked')
    else:
        print('Webhook failed')
        raise RuntimeError('Webhook failed')

def deepsleep():
    print('Going into deepsleep for {seconds} seconds...'.format(
        seconds=config.LOG_INTERVAL))
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, config.LOG_INTERVAL * 1000)
    machine.deepsleep()

def set_gate(change_state=False):
    is_open= None
    with open(config.FILENAME, 'r+') as f:
        is_open= f.read() #read current value
        is_open=bool(int(is_open))
        if change_state == True:
            next_state= "0" if is_open else "1"
            f.seek(0)
            f.write(next_state)
    return is_open

def start_motor(now, gate_state):
    #Adjust the time to avoid drift
    ntptime.settime()
    tm=utime.localtime() #In UTC
    ltime= utime.mktime((tm[0], tm[1], tm[2], tm[3]+1, tm[4], tm[5], tm[6], tm[7])) #Adds one hour from UTC
    now= utime.localtime(ltime)
    print("Check if gate need adjusting!")
    #now= time.localtime() #get current time i.e. (2019, 10, 20, 17, 20, 38, 6, 293)
    my_daylight_formula= None #formula to calculate daylight
    #now=now.timetuple()
    for period in config.DAYLIGHT:
        if period[1] > now[7]:
            my_daylight_formula= period
            break

    open_at= round( (now[7]-my_daylight_formula[0])*my_daylight_formula[2][0]+my_daylight_formula[2][1], 1 ) #8.5
    close_at= round( (now[7]-my_daylight_formula[0])*my_daylight_formula[3][0]+my_daylight_formula[3][1], 1 ) #17.5
    
    rounded_now= round(now[3]+now[4]/60., 1)
    print("now: {}, state: {}".format(rounded_now, gate_state))
    if ( (rounded_now > open_at and rounded_now < close_at) and (gate_state == False) ):
        call_webhook('Opening at {} due to open_at: {} and close_at:{}'.format(rounded_now, open_at, close_at))
        run_gate() #Opening
    elif ( (rounded_now > close_at ) and  (gate_state == True ) ):
        call_webhook('Closing at {} due to open_at: {} and close_at:{}'.format(rounded_now, open_at, close_at))
        run_gate() #Closing
    else:
        return True

def run_gate():
    print("starting motor!")
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pin_dir= machine.Pin(config.MOTOR_DIR, machine.Pin.OUT) #Rotation direction
    pwm_motor = machine.PWM(pin_motor)
    if set_gate(True):
        pin_dir.off() #Closing
    else:
        pin_dir.on() #Opening

    pwm_motor.duty(config.PWM_DUTY)
    utime.sleep(config.DOOR_TIME)
    pwm_motor.duty(768)
    utime.sleep(2)
    pwm_motor.duty(512)
    utime.sleep(2)
    pwm_motor.deinit()
    return True

def run():
    try:
        temperature, humidity = get_temperature_and_humidity()
        print('Temperature = {temperature}, Humidity = {humidity}'.format(
            temperature=temperature, humidity=humidity))
        connect_wifi()
        log_data(temperature, humidity)
        start_motor(utime.localtime(), set_gate())
    except Exception as exc:
        call_webhook(exc)
        show_error()

    if not is_debug():
        deepsleep()

run()