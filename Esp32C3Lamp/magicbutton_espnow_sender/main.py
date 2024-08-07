#### 发送端的代码
# https://docs.micropython.org/en/latest/library/espnow.html

import magicbutton
import network
import espnow
import time

MB = magicbutton.MagicButton(True)

# sta = network.WLAN(network.STA_IF)    # Enable station mode for ESP
# sta.active(True)
# sta.disconnect()        # Disconnect from last connected WiFi SSID

# 测试 esp32 的 ap 模式和 espnow 共存
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='magicbutton', authmode=network.AUTH_WPA_WPA2_PSK, password='12345678')
print(ap.ifconfig())


e = espnow.ESPNow()     # Enable ESP-NOW
e.active(True)

# 3c842747e4b8 mb sender bat

# 3c842747e4a4 mb receiver
# 64e833c9c7e8 lamp receiver
# f09e9ead2228 lamp2 receiver
peer1 = b'\x64\xe8\x33\xc9\xc7\xe8'   # MAC address of peer1's wifi interface
peer2 = b'\xf0\x9e\x9e\xad\x22\x28'  
e.add_peer(peer1)
e.add_peer(peer2)
# add peer1 (receiver1)
#如果有多个接收都就在这下面接着增加peer2...

print("esp32c3 espnow send to esp32c3lamp test...")            # Send to all peers

def btn_long_press_self_func():
    MB.ledtoggle(1)
    print("self btn long press ,power shutdown now")
    MB.powershutdown()
    
def btn_short_press_self_func():
    MB.ledtoggle(0)
    print("self btn short press ,send msg")
    e.send(peer1, "espnow sender...", True)     # send commands to pear 1
    e.send(peer2, "espnow sender...", True)

def main():
    MB.btnswitch_set_short_press_func(lambda: btn_short_press_self_func())
    MB.btnswitch_set_long_press_func(lambda: btn_long_press_self_func())
    while True:
        MB.btnswitch_scan()
        time.sleep_ms(5)

if __name__ == "__main__":
    main()


