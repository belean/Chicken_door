import dht
import machine
import network
import sys
import time
import urequests

import config
import framebuf
import ssd1306
import freesans20
import writer

def connect_wifi():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to WiFi...')
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not sta_if.isconnected():
            time.sleep(1)
    print('Network config:', sta_if.ifconfig())

def call_webhook():
    print('Invoking webhook')
    response = urequests.post(config.WEBHOOK_URL,
                              json={'value1': config.BUTTON_ID})
    if response is not None and response.status_code < 400:
        print('Webhook invoked')
    else:
        print('Webhook failed')
        raise RuntimeError('Webhook failed')

def show_error():
    led = machine.Pin(config.LED_PIN, machine.Pin.OUT)
    for i in range(3):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
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
    if config.FAHRENHEIT:
        temperature = temperature * 9 / 5 + 32
    return temperature, dht22.humidity()

def load_image(filename):
    with open(filename, 'rb') as f:
        f.readline()
        f.readline()
        width, height = [int(v) for v in f.readline().split()]
        data = bytearray(f.read())
    return framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)

def display_temperature_and_humidity(temperature, humidity):
    i2c = machine.I2C(scl=machine.Pin(config.DISPLAY_SCL_PIN),
                      sda=machine.Pin(config.DISPLAY_SDA_PIN))
    if 60 not in i2c.scan():
        raise RuntimeError('Cannot find display.')

    display = ssd1306.SSD1306_I2C(128, 64, i2c)
    font_writer = writer.Writer(display, freesans20)

    temperature_pbm = load_image('temperature.pbm')
    units_pbm = load_image('fahrenheit.pbm') if config.FAHRENHEIT \
        else load_image('celsius.pbm')
    humidity_pbm = load_image('humidity.pbm')
    percent_pbm = load_image('percent.pbm')

    display.fill(0)
    display.rect(0, 0, 128, 64, 1)
    display.line(64, 0, 64, 64, 1)
    display.blit(temperature_pbm, 24, 4)
    display.blit(humidity_pbm, 88, 4)
    display.blit(units_pbm, 28, 52)
    display.blit(percent_pbm, 92, 52)

    text = '{:.1f}'.format(temperature)
    textlen = font_writer.stringlen(text)
    font_writer.set_textpos((64 - textlen) // 2, 30)
    font_writer.printstring(text)

    text = '{:.1f}'.format(humidity)
    textlen = font_writer.stringlen(text)
    font_writer.set_textpos(64 + (64 - textlen) // 2, 30)
    font_writer.printstring(text)

    display.show()
    time.sleep(10)
    display.poweroff()

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

def check_gate():
    now= time.localtime() #get current time i.e. (2019, 10, 20, 17, 20, 38, 6, 293)
    my_daylight_formula= None #formula to calculate daylight
    for period in config.DAYLIGHT:
        if period[1] > now[7]:
            my_daylight_formula= period
            break
    open_at= round( (now[7]-my_daylight_formula[0])*my_daylight_formula[2][0]+my_daylight_formula[2][1], 1 ) #8.5
    close_at= round( (now[7]-my_daylight_formula[0])*my_daylight_formula[3][0]+my_daylight_formula[3][1], 1 ) #17.5
    if is_debug(): print("opening at {} and closing at {}".format(open_at, close_at))
    if config.CURRENT_POSITION_OPEN:
        #Check if we are closing
        if round(now[3]+now[4]/60) > close_at:
            if is_debug(): print("Closing gate!")
            run_motor(0, 3)
            config.CURRENT_POSITION_OPEN= False
    else:
        #Check if we are opening
        if round(now[3]+now[4]/60) > open_at:
            # Run motor for in other directiuon for X seconds
            if is_debug(): print("opening gate!")
            run_motor(1, 3)
            config.CURRENT_POSITION_OPEN= True

def force_run_gate():
    #Running gate has been forced by user
    if config.CURRENT_POSITION_OPEN:
        run_motor(0, 3)
        config.CURRENT_POSITION_OPEN= False
    else:
        run_motor(1, 3)
        config.CURRENT_POSITION_OPEN= True

def run_motor(dir, sec):
    # Run motor for X seconds
    if is_debug(): print("run_motor!")
    #pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    ##pin_dir= machine.Pin(0, machine.Pin.OUT)
    #pwm_motor = machine.PWM(pin_motor)
    #pwm_motor.duty(config.PWM_DUTY)

def run():
    try:
        temperature, humidity = get_temperature_and_humidity()
        print('Temperature = {temperature}, Humidity = {humidity}'.format(
            temperature=temperature, humidity=humidity))
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            # We are interactive. Show temp!
            display_temperature_and_humidity(temperature, humidity)
            force_run_gate()

        #check_gate()
        connect_wifi()
        log_data(temperature, humidity)      
    except Exception as exc:
        sys.print_exception(exc)
        show_error()

    if not is_debug():
        deepsleep()

run()