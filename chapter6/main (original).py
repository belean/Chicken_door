import dht
import framebuf
import machine
import network
import ssd1306
import sys
import time
import urequests

import config
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

def start_motor():
    # Run motor for X seconds
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    #pin_dir= machine.Pin(0, machine.Pin.OUT)
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.duty(config.PWM_DUTY)

def run():
    try:
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            temperature, humidity = get_temperature_and_humidity()
            print('Temperature = {temperature}, Humidity = {humidity}'.format(
                temperature=temperature, humidity=humidity))
            connect_wifi()
            log_data(temperature, humidity)
            display_temperature_and_humidity(temperature, humidity)
        else:
            #start_motor()
            print("Starting motor!")
    except Exception as exc:
        sys.print_exception(exc)
        show_error()

    if not is_debug():
        deepsleep()

run()