# 使用 micropython 面向对象编程的思路来定义硬件

import network
from machine import Pin,Timer,ADC
import time

# micropython 编写的按键动作识别类 按键未按下 、单双三击 长按
class Switch:
    def __init__(self, Pin, active_level = 0, long_press_time_ms = 3000, press_interval_time_ms = 500):
        # 默认低电平有效
        # 默认判定长按的阈值为3s
        # 默认连续按下间隔最长为1s
        self.pin = Pin
        self.active_level = active_level
        self.long_press_time_ms = long_press_time_ms
        self.press_interval_time_ms = press_interval_time_ms
        self.last_press_times = 1
        
        self.no_press_func = lambda: self.pass_func()  # 先将所有按下的动作函数注册为pass
        self.short_press_func = lambda: self.pass_func()
        self.double_press_func = lambda: self.pass_func()
        self.triple_press_func = lambda: self.pass_func()
        self.long_press_func = lambda: self.pass_func()
        
    def pass_func(self):
        pass
    
    def scan(self):  # 按键扫描函数
        press_times = 0  # 按下次数
        for i in range(0,3):
            if self.pin.value() == self.active_level:
                start_time_ns = time.time_ns()
                time.sleep_ms(10)  # 软件消抖延迟
                if self.pin.value() == self.active_level:
                    press_times+=1
                    while self.pin.value() == self.active_level:  # 按键按下的过程
                        time.sleep_ms(100)
                        if time.time_ns()-start_time_ns >= self.long_press_time_ms*1e6:  # 按下时间超过长按阈值，判定为长按
                            long_press_flag = 1
                            self.long_press_func()
                            while self.pin.value() == self.active_level:
                                pass
                            press_times = 0  # 按下次数清零，防止同时触发短按（包括单击、双击、三击）功能
                            i = 3
                            break
                    while self.pin.value() != self.active_level:  # 按键抬起后未按下的过程
                        time.sleep_ms(100)
                        if time.time_ns()-start_time_ns >= self.press_interval_time_ms*1e6:
                            i = 3  # 当按键抬起时间时间过长时，跳到按键次数判断部分
                            break
            else:  # 检测到未按下立刻退出，确保每次按下时i均为1，能够正常判断按下次数
                break
        if press_times == 0:
            self.no_press_func()
        elif press_times == 1:
            self.short_press_func()
        elif press_times == 2:
            self.double_press_func()
        elif press_times == 3:
            self.triple_press_func()

class MagicButton:
    def __init__(self,autoshutdown):
        self.powerpin=Pin(7,Pin.OUT) #esp32 c3 magic button 电源管理按键输出
        self.led0=Pin(3,Pin.OUT)
        self.led1=Pin(6,Pin.OUT)
        self.btnswitch=Switch(Pin(10, Pin.IN, Pin.PULL_UP))
        self.poweradc=ADC(Pin(4))
        self.poweradc.atten(ADC.ATTN_11DB)
        self.poweradc.width(ADC.WIDTH_12BIT)
        # 按键按下注册函数
        self.btnswitch.short_press_func = lambda: self.btnswitch_print_test("short press")
        self.btnswitch.double_press_func = lambda: self.btnswitch_print_test("double press")
        self.btnswitch.triple_press_func = lambda: self.btnswitch_print_test("triple press")
        self.btnswitch.long_press_func = lambda: self.btnswitch_print_test("long press")
        self.powerpin.value(1)       #上电开机
        self.powerstate=0
        if autoshutdown==True:
            self.autoshutdownenable()
    def btnswitch_print_test(self,printstr):
        print(printstr)
    # 设置按键按下注册回调函数
    def btnswitch_set_short_press_func(self,func):
        self.btnswitch.short_press_func = func
    def btnswitch_set_double_press_func(self,func):
        self.btnswitch.double_press_func = func
    def btnswitch_set_triple_press_func(self,func):
        self.btnswitch.triple_press_func = func
    def btnswitch_set_long_press_func(self,func):
        self.btnswitch.long_press_func = func
    def btnswitch_scan(self):
        self.btnswitch.scan()
    def powershutdown(self):
        self.powerpin.value(0)	# 关机
    def getpowervol(self):
        vol = self.poweradc.read_uv()
        vol = vol*2
        # 将电压值转换为伏特（保留两位小数）
        vol = vol / 1000000
        vol = round(vol, 2)
        return vol
    def autoshutdowntimer(self,tim):
        self.powerstate=self.powerstate+1
        if self.powerstate%10==0:
            print("current battery vol ：" + str(self.getpowervol()) + "V")
            print(self.powerstate)
        if self.powerstate>60:
            if self.powerstate%10==0:
                print("uptime 60s,shutdown now ,"+str(self.powerstate))
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