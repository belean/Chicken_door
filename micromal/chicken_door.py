# /Users/backis/Projects/micropython-tutorial/micro/chicken_door.py
import machine
import utime

from config import Config
from mynetwork import connect_wifi, disconnect_wifi, set_time
from utils import is_debug, sync_file, Logger, get_reset_code

config = Config()
log = Logger()


def init():
    """Turn of motor after a crash and sends logs. We don't have a state"""
    log.log_me("Entering init()!")

    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.duty(1)
    pwm_motor.deinit()

    connect_wifi()
    set_time()
    disconnect_wifi()

    # Write/read to file status
    sync_file()


def deep_sleep(schedule=None):
    """make sure to sleep and wake up at the scheduled events and sleep the rest
    schedule: The schedule for next event, only called twice a day
    state=[day_of_year, current_time[h], event_time[h], current_state]"""

    log.log_me("Entering deep_sleep()!")
    rtc = machine.RTC()
    state = rtc.memory().decode().split(',')  # state=['312','16','19','Open']
    log.log_me("With state: {}".format(rtc.memory().decode()), 1)

    if schedule:
        # new event will happen
        log.log_me("and schedule: {}".format(schedule), 1)
        if state[3] == 'Closed':
            new_event = schedule[1]
            state[3] = 'Open'
        elif state[3] == 'Open':
            new_event = schedule[0]
            state[3] = 'Closed'
        else:
            raise RuntimeError("We are neither open or closed", 3)
        state[2] = str(new_event)  # Add event to counter at state[2]

        # write to file
        with open(config.FILENAME, 'w') as fw:
            fw.seek(0, 0)
            fw.write(','.join(state))

    elif(int(state[1]) == int(state[2])-1):
        # The time is up for an event
        log.log_me("and time for event!", 1)
        state[1] = str(int(state[1])+1)
        rtc.memory(','.join(state))  # Write string to rtc memory
        return

    else:
        # times not up yet
        log.log_me("and times not up!", 1)
        current_hour = int(state[1])
        next_hour = None
        # Check of end of day
        if current_hour < 23:
            next_hour = str(current_hour + 1)
        else:
            next_hour = '0'
            log.rotate_log()  # Rotate log every day
            # Check for year end
            if (int(state[0]) >= 365):
                log.log_me("happy new year!", 1)
                state[0] = '1'
            else:
                state[0] = str(int(state[0])+1)

        state[1] = str(int(next_hour))  # Add one to counter at state[1]

    rtc.memory(','.join(state))  # Write string to rtc memory

    if not is_debug():
        log.log_me("Time for deep sleep!", 1)
        log.write_to_log()
        rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
        rtc.alarm(rtc.ALARM0, config.DEEP_SLEEP * 1000)  # set sleeping time
        machine.deepsleep()


def run_gate(state):
    """Run gate runs the gate according to the schedule"""

    log.log_me("Entering run_gate() with state: {}".format(state), 1)
    pin_motor = machine.Pin(config.MOTOR_PIN, machine.Pin.OUT)
    pin_dir = machine.Pin(config.MOTOR_DIR, machine.Pin.OUT)  # Set direction
    pwm_motor = machine.PWM(pin_motor)
    pwm_motor.freq(config.PWM_FREQ)

    my_door_time = (config.DOOR_TIME-40) if is_debug() else config.DOOR_TIME

    if state[3] == 'Open':
        pin_dir.off()  # Closing
        pwm_motor.duty(config.PWM_DUTY)
        utime.sleep(my_door_time-6)
    elif state[3] == 'Closed':
        pin_dir.on()  # Opening
        pwm_motor.duty(config.PWM_DUTY)
        utime.sleep(my_door_time)
    else:
        raise RuntimeError("We are neither open or closed", 3)

    pwm_motor.duty(768)
    utime.sleep(1)
    pwm_motor.deinit()
    return


def schedule():
    """Keeps track of all events and give main the next"""
    return config.TIMINGS2  # i.e. (7,19)


def run():
    """Is the controller that starts and checks that everything is in order"""
    log.log_me("Entering run() after reset: {}!".
               format(get_reset_code()[machine.reset_cause()]))
    rtc = machine.RTC()  # get state
    state = rtc.memory().decode().split(',')  # state=['312','16','19','Open']
    try:
        # Boot variable ##############
        # First of all check if we are to continue sleeping
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:  # 5

            # Deep sleep
            deep_sleep()

            # Run gate if we are not  sleeping anymore
            run_gate(state)

            disconnect_wifi()
            sched = schedule()  # Check Schedule for next event
            deep_sleep(sched)  # new schedule

        elif machine.reset_cause() in (machine.HARD_RESET,
                                       machine.PWRON_RESET):  # 0,6
            init()  # we have restarted but not yet set state
            state = rtc.memory().decode().split(',')
            run_gate(state)

            disconnect_wifi()
            sched = schedule()  # Check Schedule for next event
            deep_sleep(sched)  # new schedule

        else:  # We have started from a reset or a crash need to initialize
            init()
            deep_sleep()

    except Exception as exc:
        log.log_me("Exeption: {}".format(exc), 5)
        log.write_to_log()  # write log to disk
        # Reboot machine for fresh start
        machine.reset()
