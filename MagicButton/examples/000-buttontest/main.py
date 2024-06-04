'''
实验：按键检测
esp32c3 magic button
'''
from machine import Pin,Timer
import time

powerpin=Pin(7,Pin.OUT) #esp32 c3 magic button 电源管理按键输出
powerpin.value(1)       #上电开机

KEY=Pin(10,Pin.IN,Pin.PULL_UP) #构建KEY对象
state=0 #LED引脚状态
powerstate=0

print("esp32c3 magic button, button test")

#定时器
def fun(tim):
    global powerstate
    powerstate=powerstate+1
    print(powerstate)
    if powerstate>60:
        print("uptime 60s,shutdown now")
        powerpin.value(0) # 一分钟后，自动关机

#开启定时器1
tim = Timer(0)
tim.init(period=1000, mode=Timer.PERIODIC,callback=fun) # 周期1000ms


while True:
    time.sleep_ms(100)
    if KEY.value()==0:   #按键被按下
        time.sleep_ms(10) #消除抖动
        if KEY.value()==0: #确认按键被按下
            #state=not state  #使用not语句而非~语句
            #LED.value(state) #LED状态翻转
            print("button is press")
            powerstate=0
            while not KEY.value(): #检测按键是否松开
                pass