# /Users/backis/Projects/micropython-tutorial/minimal/main.py
import machine
import config
import uos
import utime

""" def get_time():
    import utime
    #Adjust the time to avoid drift
    tm=utime.localtime() #In UTC
    def my_summer_time(tm):
        if ( (tm[1]==3 && tm[6]==6 && tm[2]>24) && (tm[1]==10 && tm[6]==6 && tm[2]>24) ):
            print("+2h")
        else
            print("+1h")
    
    if ( (tm[1]>3 and tm[1]<10) or (tm[3] and (31-tm[2]) < (6-tm[6])) or (tm[3] and tm[2]==31 and tm[6]==6) ):
        print("+2h")
    else if  
     or (tm[1]==3 and tm[6]<6 and tm[2]>24) or  (tm[1]==10 and tm[6]<6 and tm[2]<24) ):


    
    ltime= utime.mktime((tm[0], tm[1], tm[2], tm[3]+1, tm[4], tm[5], tm[6], tm[7])) #Adds one hour from UTC
    return utime.localtime(ltime) """

def get_local_time():
    #Adjust the time to avoid drift
    tm=utime.localtime() #In UTC
    add_hour=1
    if( (tm[1]>3 and tm[1]<10) or ( (31-tm[2])<= 6 and (tm[6]< 6-(31-tm[2]) or tm[6]==6) ) ): #Summer time
        add_hour=2
    ltime= utime.mktime((tm[0], tm[1], tm[2], tm[3]+add_hour, tm[4], tm[5], tm[6], tm[7])) #Adds one/two hour from UTC
    return utime.localtime(ltime)

def set_time():
    import ntptime
    ntptime.settime()

def connect_wifi(lfp):
    import network
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        log_me(lfp, 'Connecting to WiFi...')
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        counter=0
        while not sta_if.isconnected():
            utime.sleep(1)
            counter+=1
            if counter > 14:
                raise RuntimeError('WLAN connection unavailable')
        log_me(lfp,'Network config: {}'.format( sta_if.ifconfig()))

def disconnect_wifi(lfp):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected():
        log_me(lfp, 'Disconnecting from WiFi...')
        sta_if.active(False)

def is_debug():
    debug = machine.Pin(config.DEBUG_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    if debug.value() == 0:
        print('Debug mode detected.')
        return True
    return False

def get_temperature_and_humidity():
    import dht
    dht22 = dht.DHT22(machine.Pin(config.DHT22_PIN))
    dht22.measure()
    temperature = dht22.temperature()
    return temperature, dht22.humidity()

def current_status(file_name, state=None):
    #Open file read unless a new state is provided
    with open(config.FILENAME, 'r+') as f:
        if state:
            f.seek(2,0)
            f.write(state)
            f.seek(0,0)
        status= f.read().split('\n')[0].split(',')
    return (status[0], status[1]) #Returns (current_timing, door status)

def adjusted_sleep(lfp, time_now, season):
    #Check for new instructions
    schedule= config.TIMINGS[season] #tuple (timepoint, seconds, seconds) for the season we are in 
    #now_timing= (time_now[3]+round(time_now[4]/60,1),) #Creating a tuple with one item
    this_morning=(time_now[0], time_now[1], time_now[2], int(schedule[0]), int(round(schedule[0]-int(schedule[0]),1)*60), time_now[5], time_now[6], time_now[7])
    next_timing=utime.mktime(this_morning)+schedule[1]-utime.mktime(time_now)
    log_me(lfp,"this_morning: {} and time_now: {} and schedule:{}".format(this_morning, time_now, season) )
    if next_timing < 0: #We're closed
        next_timing=schedule[2]-next_timing
    return next_timing

def calculate_sleep_time(lfp, direction, time_now=None):
    sleep_until= None

    if time_now: #We are either reseted or sunday at closing
        #Get the right schedule
        month=time_now[1] #Month
        season=None
        if month in (1, 2, 12): #Check if winter (jan, feb, dec)
            season=0
        else:
            season=int(month/3)

        sleep_until= adjusted_sleep(lfp, time_now, season) #Get the time from now to the next open/close event
        log_me(lfp,"Sleeping after adjustment for {sleep} seconds".format(sleep=sleep_until) )
        
        if (time_now[6]==6 and time_now[1] in [3,6,9,12] and time_now[2] < 8 and direction is 'Closed'): #Mon=0..Sun=6
            #write new timing to file
            with open(config.FILENAME, 'r+') as f:
                f.seek(0,0)
                f.write(str(season))
    else: #We are running normally
        status=current_status(config.FILENAME)
        times=config.TIMINGS[int(status[0])]    
        if direction is 'Opened':
            sleep_until= times[1]
        else:
            sleep_until= times[2]

    return sleep_until
    
def log_me(lfp, message):
    tm=get_local_time()
    tm_str= '-'.join(map(str, tm[0:3]))+'T'+':'.join(map(str, tm[3:6]))
    if is_debug():
        print('@{}: {}\n'.format(tm_str, message))
        lfp.seek(0,2) #End of file
        lfp.write('@{}: {}\n'.format(tm_str, message))
    else:
        lfp.seek(0,2) #End of file
        lfp.write('@{}: {}\n'.format(tm_str, message))

def rename_file(lfp):
    log_me(lfp, "Renaming file")
    lfp.close()
    uos.rename(config.LOGFILE, config.LOGFILE[:-3]+'bak')
    lfp=open(config.LOGFILE, 'w') #Erase file
    lfp.close()
    lfp=open(config.LOGFILE, 'r+')
    log_me(lfp, "File renamed")
    return lfp
    #uos.sync()

def send_logfile(lfp):
    import urequests
    log_me(lfp, 'Invoking webhook in send_logfile')
    lfp.flush()
    lfp.seek(0,0) #Goto first of first line in file
    reason=lfp.read() #read all lines
    response = urequests.post(config.WEBHOOK_URL,
                              json={'value1': reason})
    if response is not None and response.status_code < 400:
        log_me(lfp,'Webhook invoked')
    else:
        log_me(lfp, 'Webhook failed')
        raise RuntimeError('Webhook failed')


def deepsleep(seconds):
    #log_me(lfp, 'Going into deepsleep for {seconds} seconds...'.format(seconds=seconds))
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, seconds * 1000)
    machine.deepsleep()

def run_gate(lfp, next_state):
    #Initialize
    log_me(lfp, "starting motor! and {}".format(next_state))
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pin_dir= machine.Pin(config.MOTOR_DIR, machine.Pin.OUT) #Rotation direction
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.freq(config.PWM_FREQ)
 
    if next_state is 'Closed':
        pin_dir.off() #Closing
        pwm_motor.duty(config.PWM_DUTY)
        utime.sleep(config.DOOR_TIME-6)
    else:
        pin_dir.on() #Opening
        pwm_motor.duty(config.PWM_DUTY)
        utime.sleep(config.DOOR_TIME)

    pwm_motor.duty(768)
    utime.sleep(1)
    pwm_motor.deinit()
    return True


def run(tm=None):
    lfp=None
    sleep_seconds=0
    try:
        lfp=open(config.LOGFILE, 'r+') #Open log file
        log_me(lfp, "Wakes up and run()")
        time_now=tm if tm else get_local_time() #Set to local time if no other time provided
        #Check current status 
        status= current_status(config.FILENAME)
        log_me(lfp, "Current status: {}".format(status))
        next_state= 'Opened' if status[1] is 'Closed' else 'Closed' #Binary states

        if machine.reset_cause() == machine.DEEPSLEEP_RESET: #Wake up from deepsleep
            temperature, humidity = get_temperature_and_humidity()
            log_me(lfp, 'Temperature = {temperature}, Humidity = {humidity}'.format(
            temperature=temperature, humidity=humidity))

            if run_gate(lfp, next_state): #Run gate up or down
                current_status(config.FILENAME, next_state) #Set new state in file only if successfully run_gate()

            if time_now[6] == 6 and next_state is 'Closed': #It's sunday evening after closing
                connect_wifi(lfp)
                set_time()
                send_logfile(lfp)
                rename_file(lfp)
                sleep_seconds= calculate_sleep_time(lfp, next_state, get_local_time())

            sleep_seconds= calculate_sleep_time(lfp, next_state)
        else: #We are resetted or first started
            connect_wifi(lfp)
            set_time()
            send_logfile(lfp)  #Send log
            lfp=rename_file(lfp)
            #Open the door if closed
            if next_state is 'Opened': #Run gate up if closed
                run_gate(lfp, next_state)
                current_status(config.FILENAME, next_state) #Set new state in file only if successfully run_gate()
        
            sleep_seconds= calculate_sleep_time(lfp, next_state, get_local_time())
            #seconds=sleep_until(lfp, next_state, get_local_time())
    except Exception as exc:
        import sys
        log_me(lfp,"Exception: {}".format(exc))
        sys.print_exception(exc, file=lfp)
        connect_wifi(lfp)
        send_logfile(lfp)
        
    finally:
        disconnect_wifi(lfp)
        lfp.close()
        if not is_debug():
            deepsleep(sleep_seconds)
run()