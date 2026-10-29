# -*- coding: utf-8 -*-
"""玄机阁 · 八字命理平台 —— HTTP 服务入口（纯标准库实现）。

启动：python -m server.main [端口]   （默认 8765）
"""

import json
import mimetypes
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "web")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server import api, store  # noqa: E402
from server.api import ApiError  # noqa: E402

PORT_DEFAULT = 8766


class Handler(BaseHTTPRequestHandler):
    server_version = "XuanJiGe/1.0"
    protocol_version = "HTTP/1.1"

    # ---------- 基础 ----------
    def log_message(self, fmt, *args):
        if args and args[0] in ("GET /api/meta",):
            return
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))
        sys.stdout.flush()

    def _send(self, status, data, ctype="application/json; charset=utf-8"):
        if isinstance(data, (dict, list)):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        elif isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = data
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            raise ApiError("请求体不是合法 JSON")

    # ---------- 路由 ----------
    def do_GET(self):
        path = self.path.split("?")[0]
        try:
            if path == "/":
                return self._static("index.html")
            if path.startswith("/static/") or path.startswith("/css/") or path.startswith("/js/"):
                return self._static(path.lstrip("/"))
            if path == "/api/meta":
                return self._send(200, api.api_meta({}))
            if path == "/api/charts":
                return self._send(200, api.api_charts_list({}))
            m = re.match(r"^/api/zodiac/(\d{4})$", path)
            if m:
                return self._send(200, api.api_zodiac({"year": m.group(1)}))
            m = re.match(r"^/api/jieqi/(\d{4})$", path)
            if m:
                from server.engine import calendar_cn as cal
                table = cal.jieqi_table(int(m.group(1)))
                return self._send(200, {"year": int(m.group(1)),
                                        "terms": [{"name": n, "time": t.strftime("%Y-%m-%d %H:%M")}
                                                  for n, t in table]})
            return self._send(404, {"error": "接口不存在"})
        except ApiError as e:
            return self._send(e.status, {"error": str(e)})
        except Exception as e:
            return self._send(500, {"error": "服务器内部错误：%s" % e})

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            body = self._json_body()
            if path == "/api/paipan":
                return self._send(200, api.api_paipan(body))
            if path == "/api/analysis":
                return self._send(200, api.api_analysis(body))
            if path == "/api/fortune/year":
                return self._send(200, api.api_fortune_year(body))
            if path == "/api/fortune/today":
                return self._send(200, api.api_fortune_today(body))
            if path == "/api/charts":
                return self._send(200, api.api_charts_add(body))
            if path == "/api/ziwei":
                return self._send(200, api.api_ziwei(body))
            if path == "/api/meihua":
                return self._send(200, api.api_meihua(body))
            if path == "/api/hehun":
                return self._send(200, api.api_hehun(body))
            if path == "/api/zodiac":
                return self._send(200, api.api_zodiac(body))
            if path == "/api/astro":
                return self._send(200, api.api_astro(body))
            if path == "/api/astro/pair":
                return self._send(200, api.api_astro_pair(body))
            if path == "/api/tarot":
                return self._send(200, api.api_tarot(body))
            return self._send(404, {"error": "接口不存在"})
        except ApiError as e:
            return self._send(e.status, {"error": str(e)})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._send(500, {"error": "服务器内部错误：%s" % e})

    def do_DELETE(self):
        path = self.path.split("?")[0]
        try:
            m = re.match(r"^/api/charts/(\d+)$", path)
            if m:
                return self._send(200, api.api_charts_delete({}, int(m.group(1))))
            return self._send(404, {"error": "接口不存在"})
        except ApiError as e:
            return self._send(e.status, {"error": str(e)})
        except Exception as e:
            return self._send(500, {"error": "服务器内部错误：%s" % e})

    # ---------- 静态文件 ----------
    def _static(self, rel):
        safe = os.path.normpath(rel).replace("\\", "/")
        if safe.startswith("..") or safe.startswith("/"):
            return self._send(403, {"error": "禁止访问"})
        full = os.path.join(WEB_DIR, safe)
        if not os.path.isfile(full):
            return self._send(404, {"error": "文件不存在"})
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if full.endswith(".js"):
            ctype = "text/javascript; charset=utf-8"
        elif full.endswith(".css"):
            ctype = "text/css; charset=utf-8"
        elif full.endswith(".html"):
            ctype = "text/html; charset=utf-8"
        with open(full, "rb") as f:
            self._send(200, f.read(), ctype)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    port = PORT_DEFAULT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    store._get_conn()
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print("=" * 56)
    print("  玄机阁 · 八字排盘命理平台 v1.0")
    print("  访问地址:  http://127.0.0.1:%d" % port)
    print("  按 Ctrl+C 停止服务")
    print("=" * 56)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")


if __name__ == "__main__":
    main()
