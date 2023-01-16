# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
#import network

def wlan_start(wifimode): #options "AP" or "STA"
    import network
    if wifimode == "STA":
        ssid = None #place your ssid Here
        password = None #place your password here
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            #sta_if.config(dhcp_hostname = 'loratxt') # sets local dchp address. 
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
        print('connected to Wifi:')
        
    elif wifimode == "AP":
        ssid = 'ESP32'
        password = '123456789'
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=ssid, password=password)
        ap.active(True)
        while ap.active() == False:
            pass
        print('Connection successful')
        print(ap.ifconfig())
        
    else:
        print("You entered a option that doesnt exist, review 2 connection types")
        
        
        
wlan_start("AP")

