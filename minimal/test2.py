import chicken_door as main
import config
import utime
#"connect_wifi
#====
import network
lfp=open(config.LOGFILE, 'r+')
sta_if = network.WLAN(network.STA_IF)
main.connect_wifi(lfp)
a=sta_if.isconnected()
assert (a==True)
main.disconnect_wifi(lfp)
a=sta_if.isconnected()
assert (a==False)
lfp.close()


#send_logfile
#==============
def send_logfile2(lfp):
    import urequests
    main.log_me(lfp, 'Invoking webhook in send_logfile')
    lfp.flush()
    lfp.seek(0,0) #Goto first of first line in file
    reason=lfp.read() #read all lines
    response = urequests.post(config.WEBHOOK_URL,
                              json={'value1': reason})
    if response is not None and response.status_code < 400:
        main.log_me(lfp,'Webhook invoked')
    else:
        main.log_me(lfp, 'Webhook failed')
        raise RuntimeError('Webhook failed')

try:
    print("Open send_logfile!")
    lfp=open(config.LOGFILE, 'r+')
    main.connect_wifi(lfp)
    utime.sleep(2)
    main.send_logfile(lfp)
    lfp.close()
    print("send_logfile OK!")
except Exception as exc:
    import sys
    sys.print_exception(exc)
