from microWebSrv import MicroWebSrv
from machine import Pin
import machine
import network
import esp
import json
import magicbutton


MB = magicbutton.MagicButton(True)

# 设置自动关机时间为 5分钟
MB.set_shutdown_time(300)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='magicbutton', authmode=network.AUTH_WPA_WPA2_PSK, password='12345678')
print(ap.ifconfig())


# 获取 ESP32 系统信息

print(machine.freq() / 1000000)

unique_id = machine.unique_id()
print(unique_id)
# 核心数量通常与unique_id的第四个字节有关
# 这里我们假设unique_id的第四个字节为核心数量的指示器
#cores_count = (unique_id[3] >> 4) & 0xF

#print(f"ESP32 has {cores_count} cores.")


print(esp.flash_size())

sysdata = {
    "boardId":"magicbutton",
    "cpuFreq":str(machine.freq() / 1000000),
    }

sys_json_str = json.dumps(sysdata)

print(sys_json_str)


@MicroWebSrv.route('/index.html','GET')
def test(httpClient,httpResponse):
  t=httpClient.GetRequestMethod()
  print(t)

  content="""\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Esp32 SystemInfo</title>
    <script type="module" crossorigin src="/assets/index-19b5aa29.js"></script>
    <link rel="stylesheet" href="/assets/index-a381186d.css">
  </head>
  <body>
    <div id="app"></div>
    
  </body>
</html>
  """
  
  httpResponse.WriteResponseOk( headers         = None,
                                contentType     = "text/html",
                                contentCharset  = "UTF-8",
                                content         = content )

# GET 方法 带参数的 URL 解析
@MicroWebSrv.route('/switchLed/<status>','GET')
def switchLed(httpClient,httpResponse,args={}) :
    print(httpClient.GetIPAddr())
    if 'status' in args:
        print(str(args['status']))
        if args['status'] == 1:
            print("magicbutton,set led0(GPIO3) on")
            MB.ledctl(0,1)
        if args['status'] == 0:
            print("magicbutton,set led0(GPIO3) off")
            MB.ledctl(0,0)
    httpResponse.WriteResponseOk( headers         = None,
                                contentType     = "text/plain",
                                contentCharset  = "UTF-8",
                                content         = "ok" )


@MicroWebSrv.route('/sysInfo','GET')
def getsysInfo(httpClient,httpResponse) :
    httpResponse.WriteResponseOk( headers         = None,
                                contentType     = "application/json",
                                contentCharset  = "UTF-8",
                                content         = sys_json_str )


#srv = MicroWebSrv(webPath="")
#srv.SetNotFoundPageUrl(url="/test")
#srv.Start(threaded=True)

srv = MicroWebSrv(webPath='')
srv.Start()



