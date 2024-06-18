# 使用 micropython 面向对象编程的思路来定义硬件

import network
from machine import Pin,Timer
import time

class MagicButton:
    def __init__(self,autoshutdown):
        self.powerpin=Pin(7,Pin.OUT) #esp32 c3 magic button 电源管理按键输出
        self.led0=Pin(3,Pin.OUT)
        self.led1=Pin(6,Pin.OUT)
        self.powerpin.value(1)       #上电开机
        self.powerstate=0
        if autoshutdown==True:
            self.autoshutdownenable()
    def autoshutdowntimer(self,tim):
        self.powerstate=self.powerstate+1
        if self.powerstate%10==0:
            print(self.powerstate)
        if self.powerstate>60:
            print("uptime 60s,shutdown now")
            self.powerpin.value(0) # 一分钟后，自动关机
    def autoshutdownenable(self):
        #开启定时器1
        self.tim = Timer(0)
        self.tim.init(period=1000, mode=Timer.PERIODIC,callback=self.autoshutdowntimer) # 周期1000ms
    # led 控制
    def ledctl(self,lednum,stat):
        if lednum==0:
            self.led0.value(stat)
        if lednum==1:
            self.led1.value(stat)
    def ledtoggle(self,lednum):
        if lednum==0:
            self.led0.value(1)
            time.sleep_ms(50)
            self.led0.value(0)
        if lednum==1:
            self.led1.value(1)
            time.sleep_ms(50)
            self.led1.value(0)   
    # wifi 扫描实现
        
    def wifi_sta_enable(self,enable):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(enable)
    def wifiscan(self):
        wifilists = self.wlan.scan()
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