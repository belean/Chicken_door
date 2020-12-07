import uos
import config
import utime
import machine

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

def get_local_time():
    #Adjust the time to avoid drift
    tm=utime.localtime() #In UTC
    add_hour=1
    if( (tm[1]>3 and tm[1]<10) or ( (31-tm[2])<= 6 and (tm[6]< 6-(31-tm[2]) or tm[6]==6) ) ): #Summer time
        add_hour=2
    ltime= utime.mktime((tm[0], tm[1], tm[2], tm[3]+add_hour, tm[4], tm[5], tm[6], tm[7])) #Adds one/two hour from UTC
    return utime.localtime(ltime)

def is_debug():
    debug = machine.Pin(config.DEBUG_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    if debug.value() == 0:
        print('Debug mode detected.')
        return True
    return False

def sync_file():
    """Syncronizes files from rtc and filesystem. Since rtc erases after
    no battery we use the saved filesystem values"""
    # state=['312','16','19','Open']
    state=list() #init
    tm=get_local_time() #get current time
    with open(config.FILENAME, 'r') as f:
        f.seek(0,0)
        state= f.read().split(',')
    state[0]=str(tm[7]) #Update day
    state[1]=str(tm[3]) #and hour
    # write to rtc memory
    rtc=machine.RTC()
    rtc.memory(','.join(state))
    return state

    #write to file
    with open(config.FILENAME, 'w') as fw:
        fw.seek(0,0)
        fw.write(','.join(state))

def out_of_sync(state):
    """ Check if we can have missed an event """
    day=int(state[0])