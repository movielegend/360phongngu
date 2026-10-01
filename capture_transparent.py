import http.server
import socketserver
import threading
import subprocess
import urllib.request
import json
import base64
import time
import os
import asyncio
import websockets

PORT = 8089
os.chdir(r"D:\360")

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

httpd = socketserver.TCPServer(("127.0.0.1", PORT), QuietHandler)
server_thread = threading.Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = r"C:\Users\Admin\AppData\Local\Temp\chrome_render_k9"

proc = subprocess.Popen([
    chrome_path,
    "--headless=new",
    "--remote-debugging-port=9227",
    f"--user-data-dir={user_data}",
    "--enable-webgl",
    "--ignore-gpu-blocklist",
    "--use-gl=angle",
    "--window-size=2400,1800",
    f"http://localhost:{PORT}/render_projector.html"
])

async def capture():
    ws_url = None
    for _ in range(25):
        try:
            tabs = json.loads(urllib.request.urlopen("http://localhost:9227/json").read())
            if tabs:
                ws_url = tabs[0]["webSocketDebuggerUrl"]
                break
        except Exception:
            time.sleep(0.5)

    if not ws_url:
        raise RuntimeError("Failed to connect to Chrome debugging port")

    async with websockets.connect(ws_url) as ws:
        for _ in range(40):
            await ws.send(json.dumps({
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {"expression": "window.__RENDER_DONE__ === true"}
            }))
            res = json.loads(await ws.recv())
            if res.get("result", {}).get("result", {}).get("value") is True:
                break
            await asyncio.sleep(0.5)
        
        await ws.send(json.dumps({
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {"expression": "JSON.stringify(window.getCameraParams())"}
        }))
        res = json.loads(await ws.recv())
        if "value" in res.get("result", {}).get("result", {}):
            cam_params = res["result"]["result"]["value"]
            with open(r"D:\360\camera_params.json", "w") as f:
                f.write(cam_params)

        await ws.send(json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {"expression": "document.querySelector('canvas').toDataURL('image/png')"}
        }))
        res = json.loads(await ws.recv())
        data_url = res["result"]["result"]["value"]
        b64 = data_url.split(",")[1]
        with open(r"D:\360\projector_render_transparent.png", "wb") as f:
            f.write(base64.b64decode(b64))
        print("Transparent 2400x1800 render saved successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(capture())
    finally:
        proc.terminate()
        httpd.shutdown()
