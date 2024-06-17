# micropython wifi 扫描程序

import network
from machine import Pin,Timer
import time

powerpin=Pin(7,Pin.OUT) #esp32 c3 magic button 电源管理按键输出
powerpin.value(1)       #上电开机
powerstate=0

print("esp32c3 magic button, wifi scan test")

#定时器
def fun(tim):
    global powerstate
    powerstate=powerstate+1
    if powerstate%10==0:
        print(powerstate)
    if powerstate>60:
        print("uptime 60s,shutdown now")
        powerpin.value(0) # 一分钟后，自动关机

#开启定时器1
tim = Timer(0)
tim.init(period=1000, mode=Timer.PERIODIC,callback=fun) # 周期1000ms


wlan = network.WLAN(network.STA_IF)
wlan.active(True)


while True:
    time.sleep_ms(5000)
    wifilists = wlan.scan()
    #Scanning is only possible on STA interface. Returns list of tuples with the information about WiFi access points:
    #(ssid, bssid, channel, RSSI, authmode, hidden)
    print('扫描到的 wifi:')
    print('ssid','\t\t\t','channel','\t\t\t','rssi')
    print('----')
    for wifilist in wifilists:
        ssid = wifilist[0].decode('utf-8')
        bssid = wifilist[1]
        channel = wifilist[2]
        rssi = wifilist[3]
        print(ssid,'\t\t\t',channel,'\t\t\t',rssi)
    print('----')
    

