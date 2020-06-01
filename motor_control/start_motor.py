from datetime import datetime, timedelta
import config



def start_motor(now, gate_state):
    print("Check if gate need adjusting!")
    #now= time.localtime() #get current time i.e. (2019, 10, 20, 17, 20, 38, 6, 293)
    my_daylight_formula= None #formula to calculate daylight
    now=now.timetuple()
    for period in config.DAYLIGHT:
        if period[1] > now[7]:
            my_daylight_formula= period
            break

    open_at= round( (now[7]-my_daylight_formula[0])*my_daylight_formula[2][0]+my_daylight_formula[2][1], 1 ) #8.5
    close_at= round( (now[7]-my_daylight_formula[0])*my_daylight_formula[3][0]+my_daylight_formula[3][1], 1 ) #17.5
    
    rounded_now= round(now[3]+now[4]/60., 1)
    print("now: {}, state: {}".format(rounded_now, gate_state))

    if ( (rounded_now > open_at and rounded_now < close_at) and (gate_state == False) ):
        print("run_gate1! open:{}, close:{}".format(open_at, close_at))
    elif ( (rounded_now > close_at ) and  (gate_state == True ) ):
        print("run_gate2! open:{}, close:{}".format(open_at, close_at))
    else:
        print("Don't run! open:{}, close:{}".format(open_at, close_at))
    return

def run():
    start_motor(datetime.now(), gate_state=True)

run()