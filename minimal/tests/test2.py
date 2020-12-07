
import chicken_door as mymain
import mynetwork
import config
import utime
import urequests
import network
import utils
#connect_wifi



import network
lfp=open(config.LOGFILE, 'r+')
sta_if = network.WLAN(network.STA_IF)
mynetwork.connect_wifi(lfp)
a=sta_if.isconnected()
assert (a==True)

mynetwork.disconnect_wifi(lfp)
a=sta_if.isconnected()
assert (a==False)
lfp.close()


try:
    print("Open send_logfile!")
    lfp=open(config.LOGFILE, 'r+')
    mynetwork.connect_wifi(lfp)
    mynetwork.set_time()
    utime.sleep(2)
    mynetwork.send_logfile(lfp)
    #call_webhook()
    lfp.close()
    print("send_logfile OK!")
except Exception as exc:
    import sys
    sys.print_exception(exc)


#connect_wifi()
#call_webhook()