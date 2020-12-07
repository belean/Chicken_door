# /Users/backis/Projects/micropython-tutorial/minimal/chicken_door.py
import machine
import utime

import config
from  mynetwork import connect_wifi, disconnect_wifi, send_logfile, set_time
from utils import log_me, rename_file, get_local_time, is_debug, sync_file

def init():
    """Turn of motor after a crash and sends logs. We don't have a state"""
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.duty(1)
    pwm_motor.deinit()

    # Send log
    connect_wifi() 
    send_logfile()

    # Check for new config

    # GEt and Set time
    set_time()
 
    # Write/read to file status
    state= sync_file()

    # Are we sane i.e out of sync
    sched=schedule(state)
    if(state[3] == 'Closed' and shed[3]-1>int(state[2])> sched[2]+1):

    # Disconnct wifi
    mynetwork.disconnect_wifi()

def send_log():
    """sends the log to backis2012@gmail.com every week on sunday and after a crash"""
    pass

def deep_sleep(state, schedule=None):
    """make sure to sleep and wake up at the scheduled events and sleep the rest
    schedule: The schedule for next event, only called twice a day
    state=[day_of_year, current_time[h], event_time[h], current_state]"""
    #rtc=machine.RTC()
    #state= rtc.memory().decode().split(',') # i.e. state=['312','16','19','Open']

    if schedule: 
        # new event will happen
        if state[3] == 'Closed':
            new_event = schedule[2]
            state[3] = 'Open'
        else: 
            new_event = schedule[3]
            state[3] ='Closed'
        state[2] = str(new_event) # Add event to counter at state[2]

        #write to file
        with open(config.FILENAME, 'w') as fw:
            fw.seek(0,0)
            fw.write(','.join(state))

    elif(int(state[1]) >= int(state[2])-1):
        # The time is up for an event
        state[1] = state[2]
        rtc.memory(','.join(state)) # Write string to rtc memory
        return True

    else:
        # times not up yet
        current_hour= int(state[1])
        next_hour = None
        # Check of end of day
        if current_hour < 23:
            next_hour= str(current_hour + 1)
        else:
            next_hour= '0'
            # Check for year end
            if (int(state[0]) >= 365):
                state[0] = '1'
            else:
                state[0]= str(int(state[0])+1)

        state[1] = str(int(next_hour)) # Add one to counter at state[1]

    rtc.memory(','.join(state)) # Write string to rtc memory

    if not utils.is_debug():
        rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
        rtc.alarm(rtc.ALARM0, config.DEEP_SLEEP * 1000) #Avoid zero sleeping time
        #lfp.close() #Closing before deeepsleep
        machine.deepsleep()


def run_gate(state):
    """Run gate runs the gate according to the schedule"""

    #utils.log_me(lfp, "starting motor! and {}".format(next_state),1)
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pin_dir= machine.Pin(config.MOTOR_DIR, machine.Pin.OUT) #Rotation direction
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.freq(config.PWM_FREQ)
    
    my_door_time = (config.DOOR_TIME-40) if is_debug() else config.DOOR_TIME

    if state[3] is 'Closed':
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

def schedule(state):
    """Keeps track of all events and give main the next"""
    current_schedule=None
    for i, row in enumerate(config.TIMINGS2):
        if row[1]>=int(state[0]):
            current_schedule= config.TIMINGS2[i-1]
            break
    return current_schedule 

def get_new_config():
    """Gets a new config from the internet"""
    pass

def run():
    """Is the controller that starts and checks that everything is in order"""
    try:
       
        # Boot variable ##############
        ## First of all check if we are to continue sleeping
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
             # get state
            rtc= machine.RTC()
            state= rtc.memory().decode().split(',') # i.e. state=['312','16','19','Open']

            # Deep sleep
            deep_sleep(state)
            
            # Run gate
            run_gate(state)

        else: #We have started from a reset or a crash need to initialize
            init()


    except Exception as exc:
        print("Exeption: {}".format(exc))
        # Run init to initialize
        init()
        # Send log

        # Check for new config

    finally:
        # Disconnect
        disconnect_wifi()

         # Check Schedule for next event
        sched = schedule(state)

        # Deep sleep
        deep_sleep(state, sched)


#run()
