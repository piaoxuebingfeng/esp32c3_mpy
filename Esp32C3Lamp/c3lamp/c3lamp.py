import network
from machine import Pin,Timer
from neopixel import NeoPixel
import time
import espnow
import ubinascii

# espnow 接收端mac
# 64e833c9c7e8

#定义红、绿、蓝三种颜色
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
BLACK=(0,0,0)
WHITE=(255,255,255)

# micropython neopixel 多种灯光效果
# https://blog.csdn.net/weixin_41659040/article/details/132837911


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

class C3Lamp:
    def __init__(self):
        self.led0=Pin(6,Pin.OUT)
        self.wled0=Pin(7,Pin.OUT)
        self.wled1=Pin(12,Pin.OUT)
        self.wled0_num=8
        self.wled0mode=0  # 灯光显示模式
        self.color_pos=0
        self.sta=None
        self.e=None
        #7引脚连接灯带，灯珠数量8
        #self.np0 = NeoPixel(self.wled0, self.wled0_num)
        self.np0 = NeoPixel(self.wled0, self.wled0_num,bpp=3)
        self.btnswitch=Switch(Pin(10, Pin.IN, Pin.PULL_UP))
        # 按键按下注册函数
        self.btnswitch.short_press_func = lambda: self.switchmode()
        self.btnswitch.double_press_func = lambda: self.btnswitch_print_test("double press")
        self.btnswitch.triple_press_func = lambda: self.btnswitch_print_test("triple press")
        self.btnswitch.long_press_func = lambda: self.btnswitch_print_test("long press")
    def ledtoggle(self):
        self.led0.value(1)
        time.sleep_ms(50)
        self.led0.value(0)
    def wlan_init(self):
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.sta.disconnect()                # Disconnect from last connected WiFi SSID
        wlan_mac = self.sta.config('mac')
        print(ubinascii.hexlify(wlan_mac).decode())
    def espnow_recv_init(self):				 # espnow 接收端初始化
        self.e = espnow.ESPNow()                  # Enable ESP-NOW
        self.e.active(True)
        peer = b'\x3c\x84\x27\x47\xe4\xb8'   # MAC address of peer's wifi interface
        #这个MAC地址是发送端的
        self.e.add_peer(peer)                     # Sender's MAC registration
    def espnow_rx(self):
        host, msg = self.e.recv()
        if msg:                          # wait for message
            print(host)
            print(msg)
            self.switchmode()
    
    # 定义一个函数，用于生成一个彩虹渐变的颜色值（RGB888 格式）
    def rainbow_color(self,pos):
        # pos 是一个介于 0 到 255 的整数，表示颜色在彩虹中的位置
        # 根据 pos 的值，计算出红、绿、蓝三个分量的值（介于 0 到 255 的整数）
        if pos < 85:
            r = pos * 3
            g = 255 - pos * 3
            b = 0
        elif pos < 170:
            pos -= 85
            r = 255 - pos * 3
            g = 0
            b = pos * 3
        else:
            pos -= 170
            r = 0
            g = pos * 3
            b = 255 - pos * 3
        # 返回颜色值（RGB888 格式）
        return (r, g, b)
    # 颜色选择器
    def wheel(self,pos):
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)
    def wled0show(self,color):
        for i in range(self.wled0_num):
            self.np0[i]=color
        self.np0.write()     # 写入数据
    # 彩虹效果 所有灯光显示一个颜色 颜色渐变
    def wled0rainbow(self):
        for j in range(255):
            for i in range(self.np0.n):
                self.np0[i] = self.wheel((i+j) & 255)
            self.np0.write()
            time.sleep(0.01)
    # 彩虹渐变效果
    def wled0rainbow_show(self):
        # 定义一个变量，用于记录当前颜色在彩虹中的位置（从 0 开始）
        color_pos = self.color_pos
        # 遍历 NeoPixel 对象中的每个像素
        for i in range(self.np0.n):
            # 根据当前颜色位置生成一个彩虹渐变的颜色值（RGB888 格式）
            color = self.rainbow_color(color_pos)
            # 在 NeoPixel 对象上设置当前像素的颜色值
            self.np0[i] = color
            # 将当前颜色位置增加一定的步长（可以调节渐变效果）
            color_pos += (256 // self.np0.n + i)
            # 如果当前颜色位置超过了最大值（255），则取余数重新开始
            color_pos %= 256
        # 将 NeoPixel 对象的内容输出到 LED 条上
        self.color_pos = color_pos
        self.np0.write()
        
    # 彩色呼吸灯效果
    def wled0breatheshow(self,color,delayms):
        for i in range(0, 256, 4):
            for j in range(self.np0.n):
                self.np0[j] = (color[0] * i // 256, color[1] * i // 256, color[2] * i // 256)
            self.np0.write()
            time.sleep_ms(delayms)
        for i in range(255, -1, -4):
            for j in range(self.np0.n):
                self.np0[j] = (color[0] * i // 256, color[1] * i // 256, color[2] * i // 256)
            self.np0.write()
            time.sleep_ms(delayms)
    def wled0setcolor(self,color):
        self.np0.fill(color)
        self.np0.write()
    def wled0close(self):
        self.np0.fill(BLACK)
        self.np0.write()
    def getwled0mode(self):
        return self.wled0mode
    def switchmode(self):
        self.wled0mode = self.wled0mode+1
        if self.wled0mode >7:
            self.wled0mode=0
        print("wled0 mode:"+str(self.wled0mode))
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



