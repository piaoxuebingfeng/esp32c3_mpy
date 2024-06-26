import c3lamp
import time
import _thread


c3lamp =c3lamp.C3Lamp()


def thread_espnow_task():
    c3lamp.wlan_init()
    c3lamp.espnow_recv_init()
    while True:
        c3lamp.espnow_rx()
        time.sleep_ms(5)

def thread_btn_task():
    while True:
        c3lamp.btnswitch_scan()
        time.sleep_ms(5)

def main():
    _thread.start_new_thread(thread_btn_task, ())
    _thread.start_new_thread(thread_espnow_task, ())
    
    c3lamp.ledtoggle()
    c3lamp.wled0show((25,0,0))
    time.sleep_ms(200)
    c3lamp.wled0show((0,25,0))
    time.sleep_ms(200)
    c3lamp.wled0show((0,0,25))
    time.sleep_ms(200)
    c3lamp.wled0show((25,25,25))
    time.sleep_ms(200)
    c3lamp.wled0show((0,0,0))
    time.sleep_ms(200)
    while True:
        if c3lamp.getwled0mode() ==0:
            c3lamp.wled0rainbow_show()
            time.sleep_ms(50)
        elif c3lamp.getwled0mode() ==1:
            #彩色呼吸灯效果
            c3lamp.wled0breatheshow((255,0,255),20)
        elif c3lamp.getwled0mode() ==2:
            #彩虹效果
            c3lamp.wled0rainbow()
        elif c3lamp.getwled0mode() ==3:
            c3lamp.wled0setcolor((255,0,0))
        elif c3lamp.getwled0mode() ==4:
            c3lamp.wled0setcolor((255,255,0))
        elif c3lamp.getwled0mode() ==5:
            c3lamp.wled0setcolor((0,255,0))
        elif c3lamp.getwled0mode() ==6:
            c3lamp.wled0setcolor((255,255,255))
        elif c3lamp.getwled0mode() ==7:
            #关闭
            c3lamp.wled0close()
        time.sleep_ms(10)

if __name__ == "__main__":
    main()

