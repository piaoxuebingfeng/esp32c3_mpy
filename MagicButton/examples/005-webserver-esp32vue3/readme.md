# webserver ESP32VUE3
  这个示例提供一种方便移植的 esp32 webserver。
  
  使用 vue3 构建的前端页面，将构建完成之后的资源文件放入 esp32 文件系统中，并使用 micropython 编写一个 webserver 服务。

## web
  前端使用 vue3 编写。

```
npm install
npm run dev
npm run build
```
  构建完成之后，将会在 `web/dist` 目录下生成前端资源文件,如下。
```
assets/index-19b5aa29.js
assets/index-a381186d.css
favicon.ico
index.html
```
  将这些文件上传到 esp32 的文件系统中。

## micropython webserver
  这里使用到了 `microWebSrv.py` 库，有了这个库，可以很方便的实现 web 服务，进行前端资源推送。
  在 micropython 代码里面只需要针对前端需要的 API 编写后端代码即可。

