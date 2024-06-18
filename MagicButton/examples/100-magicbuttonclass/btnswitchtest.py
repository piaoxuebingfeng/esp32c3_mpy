import magicbutton
import time

MB = magicbutton.MagicButton(True)

def btn_long_press_self_func():
    MB.ledtoggle(1)
    print("self btn long press")



if __name__ == "__main__":
    MB.btnswitch_set_long_press_func(lambda: btn_long_press_self_func())
    MB.ledtoggle(0)
    time.sleep_ms(500)
    MB.ledtoggle(0)
    time.sleep_ms(500)
    MB.ledtoggle(1)
    time.sleep_ms(500)
    MB.ledtoggle(1)
    time.sleep_ms(500)
    while True:
        MB.btnswitch_scan()
        time.sleep_ms(5)