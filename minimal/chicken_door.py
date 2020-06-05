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

def current_status(file_name, state=None, month=None):
    #Open file read unless a new state is provided
    with open(config.FILENAME, 'r+') as f:
        f.seek(0,0)
        status= f.read().split(',')
        if state:
            status[1]=state
        if month:
            status[0]=str(month)
    if month or state:
        with open(config.FILENAME, 'w') as fw:
            fw.seek(0,0)
            fw.write(','.join(status))
    return (status[0], status[1]) #Returns (current_timing, door status)

def adjusted_sleep(lfp, time_now, month, direction):
    #Check for new instructions
    schedule= config.TIMINGS2[month] #tuple (name,timepoint, seconds,timepoint, seconds) for the month we are in 
    #now_timing= (time_now[3]+round(time_now[4]/60,1),) #Creating a tuple with one item
    this_morning=(time_now[0], time_now[1], time_now[2], int(schedule[1]), int(round(schedule[1]-int(schedule[1]),1)*60), time_now[5], time_now[6], time_now[7])
    this_evening=(time_now[0], time_now[1], time_now[2], int(schedule[3]), int(round(schedule[3]-int(schedule[3]),1)*60), time_now[5], time_now[6], time_now[7])
    time_now_secs= utime.mktime(time_now)
    this_morning_secs = utime.mktime(this_morning)
    this_evening_secs= utime.mktime(this_evening)
    log_me(lfp,"time_now_secs:{} this_morning_secs:{} this_evening_secs:{}".format(time_now_secs, this_morning_secs, this_evening_secs))
    if  time_now_secs < this_morning_secs:
        next_timing= this_morning_secs - time_now_secs + schedule[2] if direction is 'Opened' else this_morning_secs - time_now_secs
    elif time_now_secs >= this_morning_secs and time_now_secs < this_evening_secs:
        next_timing = this_evening_secs - time_now_secs if direction is 'Opened' else this_evening_secs - time_now_secs + schedule[4]
    else:
        next_timing = schedule[4] - (time_now_secs - this_evening_secs) + schedule[2] if direction is 'Opened' else schedule[4]- (time_now_secs - this_evening_secs) 

    log_me(lfp,"Direction:{} and this_morning: {} and time_now: {} and schedule:{}".format(direction, this_morning, time_now, schedule[0]) )
    return next_timing

def calculate_sleep_time(lfp, direction, time_now=None):
    sleep_until= None

    if time_now: #We are either reseted or sunday at closing
        status=current_status(config.FILENAME)
        month=int(status[0]) #Reading from file

        sleep_until= adjusted_sleep(lfp, time_now, month, direction) #Get the time from now to the next open/close event
        log_me(lfp,"Sleeping after adjustment for {sleep} seconds".format(sleep=sleep_until),1 )
        
        if (time_now[6]==6 and time_now[2] < 8 and direction is 'Closed'): #Mon=0..Sun=6
            #write new timing to file
            current_status(config.FILENAME, state=None, month=time_now[1])

    else: #We are running normally
        status=current_status(config.FILENAME)
        times=config.TIMINGS2[int(status[0])]    
        if direction is 'Opened':
            sleep_until= times[2]
        else:
            sleep_until= times[4]

    return sleep_until
    
def log_me(lfp, message, log=0):
    tm=get_local_time()
    tm_str= '-'.join(map(str, tm[0:3]))+'T'+':'.join(map(str, tm[3:6]))
    if is_debug():
        print('@{}: {}\n'.format(tm_str, message))
    elif log >= config.LOGLEVEL:
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
        log_me(lfp,'Webhook invoked',1)
    else:
        log_me(lfp, 'Webhook failed',1)
        raise RuntimeError('Webhook failed')


def deepsleep(seconds=None):
    #log_me(lfp, 'Going into deepsleep for {seconds} seconds...'.format(seconds=seconds))
    #Needs to keep track of max sleep time ~71 min
    rtc = machine.RTC()
    if seconds: #We are called for the first time
        rtc.memory(b'{}'.format(seconds))
    else:
        time_to_sleep=rtc.memory(str(int(rtc.memory())-config.DEEP_SLEEP)) #We already slept for config.DEEP_SLEEP

    if time_to_sleep < config.DEEP_SLEEP:
        rtc.memory(b'')
    else:
        time_to_sleep=config.DEEP_SLEEP

    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, time_to_sleep * 1000)
    machine.deepsleep()

def run_gate(lfp, next_state):
    #Initialize
    log_me(lfp, "starting motor! and {}".format(next_state),1)
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pin_dir= machine.Pin(config.MOTOR_DIR, machine.Pin.OUT) #Rotation direction
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.freq(config.PWM_FREQ)
    
    my_door_time = (config.DOOR_TIME-40) if is_debug() else config.DOOR_TIME

    if next_state is 'Closed':
        pin_dir.off() #Closing
        pwm_motor.duty(config.PWM_DUTY)
        utime.sleep(my_door_time-6)
    else:
        pin_dir.on() #Opening
        pwm_motor.duty(config.PWM_DUTY)
        utime.sleep(my_door_time)

    pwm_motor.duty(768)
    utime.sleep(1)
    pwm_motor.deinit()
    return True

def stop_gate(lfp):
    log_me(lfp, "Stopping motor!",1)
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.duty(768)
    utime.sleep(1)
    pwm_motor.deinit()

def run(tm=None):
    lfp=None
    sleep_seconds=0
   
    #First of all check if we are to continue sleeping
    if machine.reset_cause == machine.DEEPSLEEP_RESET:
        deepsleep()
    
    try:
        lfp=open(config.LOGFILE, 'r+') #Open log file
        log_me(lfp, "Wakes up and run()",1)
        time_now=tm if tm else get_local_time() #Set to local time if no other time provided
        #Check current status 
        status= current_status(config.FILENAME)
        log_me(lfp, "Current status: {}".format(status),1)
        next_state= 'Opened' if status[1] is 'Closed' else 'Closed' #Binary states

        if machine.reset_cause() in [ machine.PWRON_RESET, machine.HARD_RESET, 
                                    machine.WDT_RESET, machine.SOFT_RESET ]: #We are resetted or first started
            connect_wifi(lfp)
            set_time()
            send_logfile(lfp)  #Send log
            lfp=rename_file(lfp)
            #Open the door if closed
            #if next_state is 'Opened': #Run gate up if closed
            run_gate(lfp, next_state)
            current_status(config.FILENAME, next_state) #Set new state in file only if successfully run_gate()
            #Sleep to next scheduled event
            sleep_seconds= calculate_sleep_time(lfp, next_state, get_local_time())
            #seconds=sleep_until(lfp, next_state, get_local_time())
            
        else: #Wake up from deepsleep
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
    except Exception as exc:
        import sys
        log_me(lfp, "Exception: {}".format(exc), 5)
        sys.print_exception(exc, lfp)
        connect_wifi(lfp)
        send_logfile(lfp)
        
    finally:
        disconnect_wifi(lfp)
        stop_gate(lfp)
        lfp.close()
        if not is_debug():
            deepsleep(sleep_seconds)
#run()