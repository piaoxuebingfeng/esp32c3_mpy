#### 发送端的代码

import magicbutton
import network
import espnow
import time

MB = magicbutton.MagicButton(True)

sta = network.WLAN(network.STA_IF)    # Enable station mode for ESP
sta.active(True)
sta.disconnect()        # Disconnect from last connected WiFi SSID

e = espnow.ESPNow()     # Enable ESP-NOW
e.active(True)

# 3c842747e4b8 mb sender bat

# 3c842747e4a4 mb receiver

peer1 = b'\x3c\x84\x27\x47\xe4\xa4'   # MAC address of peer1's wifi interface
e.add_peer(peer1)                     # add peer1 (receiver1)
#如果有多个接收都就在这下面接着增加peer2...

print("Starting...")            # Send to all peers

def main():
    while True:
        e.send(peer1, "espnow sender...", True)     # send commands to pear 1
        MB.ledtoggle(0)
        time.sleep(2)

if __name__ == "__main__":
    main()


