# /Users/backis/Projects/micropython-tutorial/minimal/chicken_door.py
import machine
import config
import utime
import mynetwork
import utils

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
    utils.log_me(lfp,"time_now_secs:{} this_morning_secs:{} this_evening_secs:{}".format(time_now_secs, this_morning_secs, this_evening_secs))
    if  time_now_secs < this_morning_secs:
        next_timing= this_morning_secs - time_now_secs + schedule[2] if direction is 'Opened' else this_morning_secs - time_now_secs
    elif time_now_secs >= this_morning_secs and time_now_secs < this_evening_secs:
        next_timing = this_evening_secs - time_now_secs if direction is 'Opened' else this_evening_secs - time_now_secs + schedule[4]
    else:
        next_timing = schedule[4] - (time_now_secs - this_evening_secs) + schedule[2] if direction is 'Opened' else schedule[4]- (time_now_secs - this_evening_secs) 

    utils.log_me(lfp,"Direction:{} and this_morning: {} and time_now: {} and schedule:{}".format(direction, this_morning, time_now, schedule[0]) )
    return next_timing

def calculate_sleep_time(lfp, direction, time_now=None):
    sleep_until= None

    if time_now: #We are either reseted or sunday at closing
        status=current_status(config.FILENAME)
        month=int(status[0]) #Reading from file

        sleep_until= adjusted_sleep(lfp, time_now, month, direction) #Get the time from now to the next open/close event
        utils.log_me(lfp,"Sleeping after adjustment for {sleep} seconds".format(sleep=sleep_until),1 )
        
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
    
def deepsleep_util(seconds=None):
    rtc = machine.RTC()
    if not seconds: #We are not called for the first time
        remaining_time=0 if rtc.memory()==b'' else int(rtc.memory())
        seconds = remaining_time-config.DEEP_SLEEP #We already slept for config.DEEP_SLEEP
    
    if seconds > config.DEEP_SLEEP:
        rtc.memory(b'{}'.format(seconds))
        return config.DEEP_SLEEP
    else:
        rtc.memory(b'') #Reset the counter
        return seconds if seconds > 0 else 0

def deepsleep(seconds=None):
    #utils.log_me(lfp, 'Going into deepsleep for {seconds} seconds...'.format(seconds=seconds))
    #Needs to keep track of max sleep time ~71 min
    #lfp=open(config.LOGFILE, 'r+')
    if seconds:
        #utils.log_me(lfp, 'Seconds: {}'.format(seconds))
        time_to_sleep=deepsleep_util(seconds) #1st run
    else:
        time_to_sleep=deepsleep_util() #Repeat
    
    #utils.log_me(lfp, 'time_to_sleep: {}'.format(time_to_sleep))

    if time_to_sleep <= 300:
        #lfp.close()
        return 0 #No need for sleep if we only have 300 seconds left
    else:
        rtc = machine.RTC()
        rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
        rtc.alarm(rtc.ALARM0, time_to_sleep * 1000) #Avoid zero sleeping time
        #lfp.close() #Closing before deeepsleep
        machine.deepsleep()

def run_gate(lfp, next_state):
    #Initialize
    utils.log_me(lfp, "starting motor! and {}".format(next_state),1)
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pin_dir= machine.Pin(config.MOTOR_DIR, machine.Pin.OUT) #Rotation direction
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.freq(config.PWM_FREQ)
    
    my_door_time = (config.DOOR_TIME-40) if utils.is_debug() else config.DOOR_TIME

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
    utils.log_me(lfp, "Stopping motor!",1)
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.duty(768)
    utime.sleep(1)
    pwm_motor.deinit()

def run(tm=None):
    lfp=None
    sleep_seconds=0
   
    #First of all check if we are to continue sleeping
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        deepsleep()
    
    try:
        lfp=open(config.LOGFILE, 'r+') #Open log file
        utils.log_me(lfp, "Wakes up and run() with reset_cause: {}".format(machine.reset_cause()),1)
        time_now=tm if tm else utils.get_local_time() #Set to local
        #Check current status 
        status= current_status(config.FILENAME)
        utils.log_me(lfp, "Current status: {}".format(status),1)
        next_state= 'Opened' if status[1] is 'Closed' else 'Closed' #Binary states

        if machine.reset_cause() in [ machine.PWRON_RESET, machine.HARD_RESET, 
                                    machine.WDT_RESET, machine.SOFT_RESET ]: #We are first started
            mynetwork.connect_wifi(lfp)
            mynetwork.set_time()
            mynetwork.send_logfile(lfp)  #Send log
            #lfp=utils.rename_file(lfp)
            #Open the door if closed
            #if next_state is 'Opened': #Run gate up if closed
            run_gate(lfp, next_state)
            current_status(config.FILENAME, next_state) #Set new state in file only if successfully run_gate()
            #Sleep to next scheduled event
            sleep_seconds= calculate_sleep_time(lfp, next_state, time_now)
            #seconds=sleep_until(lfp, next_state, utils.get_local_time())
            
        else: #Wake up from deepsleep
            temperature, humidity = get_temperature_and_humidity()
            utils.log_me(lfp, 'Temperature = {temperature}, Humidity = {humidity}'.format(
            temperature=temperature, humidity=humidity))

            run_gate(lfp, next_state) #Run gate up or down
            current_status(config.FILENAME, next_state) #Set new state in file only if successfully run_gate()

            if time_now[6] == 6 and next_state is 'Closed': #It's sunday evening after closing
                mynetwork.connect_wifi(lfp)
                mynetwork.set_time()
                mynetwork.send_logfile(lfp)
                utils.rename_file(lfp)
                sleep_seconds= calculate_sleep_time(lfp, next_state, tm)

            sleep_seconds= calculate_sleep_time(lfp, next_state)
        utils.log_me(lfp, "Sleeping for {} seconds!".format(sleep_seconds))
    except Exception as exc:
        import sys
        utils.log_me(lfp, "Exception: {}".format(exc), 5)
        sys.print_exception(exc, lfp)
        mynetwork.connect_wifi(lfp)
        mynetwork.send_logfile(lfp)
    finally:
        mynetwork.disconnect_wifi(lfp)
        stop_gate(lfp)
        lfp.close()

    if not utils.is_debug():
            deepsleep(sleep_seconds)
        
#run()