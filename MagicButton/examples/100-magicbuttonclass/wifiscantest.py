import magicbutton
import time


MB = magicbutton.MagicButton(True)

MB.wifi_sta_enable(True)




if __name__ == "__main__":
    MB.ledctl(0,True)
    MB.ledctl(1,False)
    time.sleep_ms(500)
    MB.ledctl(0,False)
    MB.ledctl(1,True)
    time.sleep_ms(500)
    MB.ledctl(0,True)
    MB.ledctl(1,False)
    time.sleep_ms(500)
    MB.ledctl(0,False)
    MB.ledctl(1,True)
    time.sleep_ms(500)
    MB.ledctl(0,False)
    MB.ledctl(1,False)
    MB.ledtoggle(0)
    time.sleep_ms(500)
    MB.ledtoggle(0)
    time.sleep_ms(500)
    MB.ledtoggle(1)
    time.sleep_ms(500)
    MB.ledtoggle(1)
    time.sleep_ms(500)

    while True:
        MB.wifiscan()
        time.sleep_ms(5000)
