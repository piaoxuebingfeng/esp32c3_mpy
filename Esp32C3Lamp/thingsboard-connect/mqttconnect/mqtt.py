import network
#from umqtt.simple import MQTTClient
from umqtt.robust import MQTTClient
from machine import Pin
import time
import _thread
import json
import gc
import ntptime
from machine import Timer
import utime




ssid = 'ssid'
password = 'password'


client_id = ""
tb_ip     = "hostip"
tb_port   = 1883
tb_access_token = "tb_device_token"
tb_password = ""


client = None
con_ok = False
switch = False
redvalue = 0
gpiostatus = False
timercount = 0

led0=Pin(6,Pin.OUT)

led0.on()                  #灯打开
time.sleep(1)             #延时一秒
led0.off()                 #灯关闭
time.sleep(1)#延时一秒




wlan = network.WLAN(network.STA_IF)


def connect_wifi():
    global wlan
    wlan.active(True)
    wlan.connect(ssid,password)

    while not wlan.isconnected():
        pass
    print('wlan connected')
    print('wifi info:')
    print(wlan.ifconfig())



def sync_ntp():
    """通过网络校准时间"""
    if wlan.isconnected():
        print("start ntp sync")
        try:
            ntptime.NTP_DELTA = 3155644800  # 可选 UTC+8偏移时间（秒），不设置就是UTC0
            #ntptime.host = 'ntp1.aliyun.com'  # 可选，ntp服务器，默认是"pool.ntp.org" 这里使用阿里服务器
            ntptime.host = 'ntp4.aliyun.com'
            ntptime.settime()  # 修改设备时间,到这就已经设置好了
        except Exception as e:
            print("ntp sync error,",repr(e))
        print("ntp sync end")
    else:
        print("wifi connect failed,please connect wifi first")


def mqtt_publish(topic,msg):
    client.publish(topic,msg)
    
    
def tb_send_tele(dic):
    if con_ok :
        msg = json.dumps(dic)
        mqtt_publish("v1/devices/me/telemetry", json.dumps(dic))
    else:
        print("pub tele failed")
def tb_send_attr(dic):
    if con_ok :
        msg = json.dumps(dic)
        mqtt_publish("v1/devices/me/attributes", json.dumps(dic))
    else:
        print("pub attr failed")

def sub_callback(topic, msg):
    global switch,redvalue,gpiostatus
    topic = topic.decode()
    msg = msg.decode()
    print((topic, msg))
    if topic.startswith("v1/devices/me/rpc/request/"):
        reqid = topic[len("v1/devices/me/rpc/request/"):]
        print(reqid)
        data=json.loads(msg)
        print(data)
        if(data["method"]=="setValue"):
            switch = data["params"]
            if switch == True:
                led0.on()
            elif switch == False:
                led0.off()
            data={"value":switch}
            mqtt_publish(f"v1/devices/me/rpc/response/{reqid}", json.dumps(data))
        elif (data["method"]=="getValue"):
            data={"value":switch}
            mqtt_publish(f"v1/devices/me/rpc/response/{reqid}", json.dumps(data))
        elif (data["method"]=="setRedValue"):
            redvalue = data["params"]
            print("redvaule:",redvalue)
            data={"value":redvalue}
            mqtt_publish(f"v1/devices/me/rpc/response/{reqid}", json.dumps(data))
        elif (data["method"]=="getRedValue"):
            data={"value":redvalue}
            print(data)
            mqtt_publish(f"v1/devices/me/rpc/response/{reqid}", json.dumps(data))

def mqtt_connect():
    global client
    global con_ok
    # MQTTClient参数说明
    # MQTTClient(client_id,server,port=0,user=None,password=None,keepalive=0,ssl=None)
    client = MQTTClient(client_id, tb_ip , tb_port,tb_access_token,tb_password,keepalive=5)#修改实际的ip 和token
    client.set_callback(sub_callback)
    client.connect()
    client.subscribe("v1/devices/me/rpc/request/+")
    client.subscribe("v1/devices/me/attributes")
    print("mqtt connected")
    con_ok = True



def reconnect():
    global con_ok
    if not wlan.isconnected():
        con_ok = False
        print("[reconnect] wifi reconnecting")
        connect_wifi()
        print("[reconnect] mqtt client reconnecting")
        mqtt_connect()
    # 	AttributeError: 'MQTTClient' object has no attribute 'isconnected'
    #if not client.isconnected():
    #   print("[reconnect] mqtt client reconnecting")
    #    mqtt_connect()
        
def thread_reconnect():
    time.sleep(10)
    print("reconnect thread start")
    while True:
        reconnect()
        time.sleep(1)

_thread.start_new_thread(thread_reconnect, ())



def timer_callback(tim):
    global timercount
    print("timer_callback timercount:",timercount)
    timercount = timercount +1
    if(timercount > 60*5):
        print("5 hours timer ,start ntp sync")
        sync_ntp()
        timercount = 0
    # 一分钟上报一次时间戳信息
    send_dict={}
    send_dict["timermsg"]=time.localtime()
    print(send_dict)
    tb_send_tele(send_dict)

timer = Timer(0)
# 定时一分钟
timer.init(period=1000*60, mode=Timer.PERIODIC, callback=timer_callback)



if __name__ == "__main__":
    print("esp32c3 mqtt test demo")
    print("connect thingsboard")
    connect_wifi()
    
    if wlan.isconnected():
        sync_ntp()
        
        mqtt_connect()
        
        time.sleep(1)
        tb_send_attr({"memory":gc.mem_free()})
        tb_send_tele({"voltage":3.80,"current":3.1,
              "soc":99,"temperature":20})
        counter = 0
        while True:
            try:
                client.wait_msg()
                #client.check_msg()
                #print(counter)
                #counter = counter +1
                #client.ping()
                #time.sleep(1)
            except OSError as e:
                print("client wait_msg error,",repr(e))
                reconnect()
                    
