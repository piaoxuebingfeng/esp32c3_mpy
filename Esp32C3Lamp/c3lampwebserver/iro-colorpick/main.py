from microWebSrv import MicroWebSrv
from machine import Pin
from neopixel import NeoPixel
import network


    
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='c3lamp', authmode=network.AUTH_WPA_WPA2_PSK, password='12345678')
print(ap.ifconfig())


def set_led(rgb):
  pin = Pin(7, Pin.OUT)   # set GPIO0 to output to drive NeoPixels
  np = NeoPixel(pin, 8)   # create NeoPixel driver on GPIO0 for 8 pixels
  for x in range(8):
    np[x]=rgb
  np.write()              # write data to all pixels



import random
def set_random():
  pin = Pin(7, Pin.OUT)   # set GPIO0 to output to drive NeoPixels
  np = NeoPixel(pin, 8)   # create NeoPixel driver on GPIO0 for 8 pixels
  for x in range(8):
    r=random.randint(0,100)
    g=random.randint(0,100)
    b=random.randint(0,100)
    np[x]=(r,g,b)
  np.write()            # write data to all pixels



  
@MicroWebSrv.route('/test/','GET')
def test(httpClient,httpResponse):
  t=httpClient.GetRequestMethod()
  print(t)

  content="""\
  <!DOCTYPE html>
  <html>
  <script src="/iro.min.js"></script>
  <script src="/jquery.min.js"></script>
  <body>
      <div id="picker"></div>
  </body>
  <script type="text/javascript">
      var colorPicker = new iro.ColorPicker("#picker", {
      //设置颜色选择器的大小
      width: 160,
      //将初始颜色设置为纯红色
      color: "#f00"
      });
      //收听颜色选择器的color:change事件
      //color:change回调接收当前颜色
      colorPicker.on('color:change', function(color) {
      //将当前颜色记录为十六进制字符串
      console.log(color.hexString);
            $.ajax({
                url: "/test/",
                type: "POST",
                datatype: "json",
                data: JSON.stringify({"code":color.rgb}),
                success: function (callback) {
                    console.log(callback);
                }

            });
      });
  </script>
  </html>
  """
  # {"code":color.rgb}
  # {"code":{"r":56,"g":242,"b":255}}
  
  httpResponse.WriteResponseOk( headers         = None,
                                contentType     = "text/html",
                                contentCharset  = "UTF-8",
                                content         = content )


@MicroWebSrv.route('/test/','POST')
def test_(httpClient,httpResponse):
  #print(httpClient.ReadRequestContent())
  data=httpClient.ReadRequestContentAsJSON()
  print(data)
  r=int(data['code']['r']/10)
  g=int(data['code']['g']/10)
  b=int(data['code']['b']/10)
  print(r,g,b)
  set_led((r,g,b))
  
  httpResponse.WriteResponseRedirect('/test/')



#srv = MicroWebSrv(webPath="")
#srv.SetNotFoundPageUrl(url="/test")
#srv.Start(threaded=True)

srv = MicroWebSrv(webPath='')
srv.Start()



