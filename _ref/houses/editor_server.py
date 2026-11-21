# -*- coding: utf-8 -*-
"""本地房屋编辑器后端：读写 houses_data.json + 触发 gen_all_houses.py 重出图。
启动：python editor_server.py  然后浏览器打开 http://127.0.0.1:8765/
"""
import os
import sys
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "houses_data.json")
HTML_PATH = os.path.join(HERE, "editor.html")
GEN_PATH = os.path.join(HERE, "gen_all_houses.py")
PORT = 8765


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode("utf-8") if n else "{}"

    def do_GET(self):
        p = self.path.split("?", 1)[0]
        if p in ("/", "/index.html"):
            with open(HTML_PATH, "r", encoding="utf-8") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if p == "/api/data":
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                return self._send(200, json.load(f))
        if p == "/api/status":
            return self._send(200, {"ok": True, "data": DATA_PATH, "gen": GEN_PATH})
        return self._send(404, {"ok": False, "error": "not found: " + p})

    def do_POST(self):
        p = self.path.split("?", 1)[0]
        if p == "/api/data":
            raw = self._body()
            try:
                obj = json.loads(raw)
                assert isinstance(obj, list), "顶层必须是数组"
                # 原子写：先写临时文件再替换，避免中途崩溃毁数据
                tmp = DATA_PATH + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(obj, f, ensure_ascii=False, indent=2)
                os.replace(tmp, DATA_PATH)
                return self._send(200, {"ok": True, "count": len(obj)})
            except Exception as e:
                return self._send(400, {"ok": False, "error": str(e)})
        if p == "/api/regen":
            try:
                r = subprocess.run([sys.executable, GEN_PATH], cwd=HERE,
                                   capture_output=True, text=True, timeout=120)
                out = (r.stdout or "") + (r.stderr or "")
                return self._send(200, {"ok": r.returncode == 0,
                                        "code": r.returncode, "out": out[-4000:]})
            except Exception as e:
                return self._send(500, {"ok": False, "error": str(e)})
        return self._send(404, {"ok": False, "error": "not found: " + p})

    def log_message(self, fmt, *args):
        pass  # 静音，别刷屏


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("house editor -> http://127.0.0.1:%d/  (Ctrl+C to stop)" % PORT)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
