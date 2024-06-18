#### 接收端的代码

import magicbutton
import network
import espnow
# 3c842747e4b8 mb sender bat
# 3c842747e4a4 mb receiver

MB = magicbutton.MagicButton(True)

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()                # Disconnect from last connected WiFi SSID

e = espnow.ESPNow()                  # Enable ESP-NOW
e.active(True)

peer = b'\x3c\x84\x27\x47\xe4\xb8'   # MAC address of peer's wifi interface
#这个MAC地址是发送端的
e.add_peer(peer)                     # Sender's MAC registration

def espnow_rx():
    while True:
        host, msg = e.recv()
        if msg:                          # wait for message
            MB.ledtoggle(1)
            print(host)
            print(msg)
if __name__ == "__main__":
    espnow_rx()
    
    
    


