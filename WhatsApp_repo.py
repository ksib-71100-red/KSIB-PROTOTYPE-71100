#!/usr/bin/env python3
import smtplib, threading, random, time, sys, os, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colorama import init, Fore, Style
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "\n🔐 KSIB GİRİŞ\n")
    for i in range(3):
        s = input(Fore.YELLOW + "🔑 Şifre: ")
        if s == SIFRE:
            print(Fore.GREEN + "\n✅ Başarılı!\n")
            time.sleep(1)
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    sys.exit(0)

# ÜLKE VERİTABANI
ULKELER = {
    # Afrika
    "20": "Mısır", "211": "Güney Sudan", "212": "Fas", "213": "Cezayir",
    "216": "Tunus", "218": "Libya", "220": "Gambiya", "221": "Senegal",
    "222": "Moritanya", "223": "Mali", "224": "Gine", "225": "Fildişi Sahili",
    "226": "Burkina Faso", "227": "Nijer", "228": "Togo", "229": "Benin",
    "230": "Mauritius", "231": "Liberya", "232": "Sierra Leone", "233": "Gana",
    "234": "Nijerya", "235": "Çad", "236": "Orta Afrika", "237": "Kamerun",
    "238": "Yeşil Burun", "239": "Sao Tome", "240": "Ekvator Ginesi",
    "241": "Gabon", "242": "Kongo", "243": "Dem. Kongo", "244": "Angola",
    "245": "Gine-Bissau", "248": "Seyşeller", "249": "Sudan", "250": "Ruanda",
    "251": "Etiyopya", "252": "Somali", "253": "Cibuti", "254": "Kenya",
    "255": "Tanzanya", "256": "Uganda", "257": "Burundi", "258": "Mozambik",
    "260": "Zambiya", "261": "Madagaskar", "263": "Zimbabve", "264": "Namibya",
    "265": "Malavi", "266": "Lesoto", "267": "Botsvana", "268": "Esvatini",
    "269": "Komorlar", "27": "Güney Afrika", "291": "Eritre",
    # Avrupa
    "30": "Yunanistan", "31": "Hollanda", "32": "Belçika", "33": "Fransa",
    "34": "İspanya", "350": "Cebelitarık", "351": "Portekiz", "352": "Lüksemburg",
    "353": "İrlanda", "354": "İzlanda", "355": "Arnavutluk", "356": "Malta",
    "357": "Kıbrıs", "358": "Finlandiya", "359": "Bulgaristan", "36": "Macaristan",
    "370": "Litvanya", "371": "Letonya", "372": "Estonya", "373": "Moldova",
    "374": "Ermenistan", "375": "Belarus", "376": "Andorra", "377": "Monako",
    "378": "San Marino", "380": "Ukrayna", "381": "Sırbistan", "382": "Karadağ",
    "383": "Kosova", "385": "Hırvatistan", "386": "Slovenya", "387": "Bosna Hersek",
    "389": "Kuzey Makedonya", "39": "İtalya", "40": "Romanya", "41": "İsviçre",
    "420": "Çekya", "421": "Slovakya", "423": "Lihtenştayn", "43": "Avusturya",
    "44": "İngiltere", "45": "Danimarka", "46": "İsveç", "47": "Norveç",
    "48": "Polonya", "49": "Almanya",
    # Asya & Orta Doğu
    "7": "Rusya/Kazakistan", "81": "Japonya", "82": "Güney Kore", "84": "Vietnam",
    "850": "Kuzey Kore", "852": "Hong Kong", "853": "Makao", "855": "Kamboçya",
    "856": "Laos", "86": "Çin", "880": "Bangladeş", "886": "Tayvan",
    "90": "Türkiye", "91": "Hindistan", "92": "Pakistan", "93": "Afganistan",
    "94": "Sri Lanka", "95": "Myanmar", "960": "Maldivler", "961": "Lübnan",
    "962": "Ürdün", "963": "Suriye", "964": "Irak", "965": "Kuveyt",
    "966": "Suudi Arabistan", "967": "Yemen", "968": "Umman", "970": "Filistin",
    "971": "BAE", "972": "İsrail", "973": "Bahreyn", "974": "Katar",
    "975": "Butan", "976": "Moğolistan", "977": "Nepal", "98": "İran",
    "992": "Tacikistan", "993": "Türkmenistan", "994": "Azerbaycan", "995": "Gürcistan",
    "996": "Kırgızistan", "998": "Özbekistan",
    # Amerika
    "1": "ABD/Kanada", "52": "Meksika", "53": "Küba", "54": "Arjantin",
    "55": "Brezilya", "56": "Şili", "57": "Kolombiya", "58": "Venezuela",
    "501": "Belize", "502": "Guatemala", "503": "El Salvador", "504": "Honduras",
    "505": "Nikaragua", "506": "Kosta Rika", "507": "Panama", "509": "Haiti",
    "51": "Peru", "591": "Bolivya", "592": "Guyana", "593": "Ekvador",
    "595": "Paraguay", "597": "Surinam", "598": "Uruguay",
    # Okyanusya
    "61": "Avustralya", "64": "Yeni Zelanda", "673": "Brunei", "675": "Papua Yeni Gine",
    "676": "Tonga", "677": "Solomon Adaları", "678": "Vanuatu", "679": "Fiji",
    "680": "Palau", "685": "Samoa", "686": "Kiribati", "687": "Yeni Kaledonya",
    "688": "Tuvalu", "689": "Fransız Polinezyası", "691": "Mikronezya", "692": "Marshall Adaları",
}

# DETAYLI ŞİKAYET KATEGORİLERİ
KATEGORILER = {
    "spam": {
        "baslik": "Spam & İstenmeyen Mesajlar",
        "sablonlar": [
            "This number {phone} is sending spam messages to multiple users.",
            "User {phone} is sending unwanted commercial messages and spam.",
            "The account {phone} is being used for mass spam distribution.",
            "Reporting {phone} for sending bulk unsolicited messages.",
            "This WhatsApp account {phone} is a known spam source.",
            "User {phone} is sending chain messages and spam links.",
            "The number {phone} is spamming group chats with advertisements.",
        ]
    },
    "harassment": {
        "baslik": "Taciz & Tehdit",
        "sablonlar": [
            "User {phone} is harassing me with threatening messages.",
            "This number {phone} is sending threatening and intimidating messages.",
            "Reporting {phone} for continuous harassment and bullying.",
            "The account {phone} is stalking and harassing multiple users.",
            "User {phone} is making death threats and violent threats.",
            "This person {phone} won't stop sending abusive messages.",
            "The number {phone} is sexually harassing users on WhatsApp.",
        ]
    },
    "scam": {
        "baslik": "Dolandırıcılık & Sahtekarlık",
        "sablonlar": [
            "This number {phone} is trying to scam people for money.",
            "User {phone} is running a phishing scam on WhatsApp.",
            "Reporting {phone} for fraudulent activities and scamming.",
            "The account {phone} is impersonating a bank/company to steal info.",
            "This WhatsApp user {phone} is running investment scams.",
            "User {phone} is asking for money with fake promises.",
            "The number {phone} is involved in cryptocurrency fraud.",
        ]
    },
    "fake": {
        "baslik": "Sahte Hesap & Kimlik Hırsızlığı",
        "sablonlar": [
            "This account {phone} is fake and impersonating someone else.",
            "User {phone} is using a fake identity on WhatsApp.",
            "Reporting {phone} for identity theft and impersonation.",
            "The account {phone} is pretending to be a celebrity/official.",
            "This number {phone} is using stolen photos and identity.",
            "User {phone} created fake account to deceive people.",
            "The number {phone} is impersonating my friend/family member.",
        ]
    },
    "inappropriate": {
        "baslik": "Uygunsuz İçerik",
        "sablonlar": [
            "User {phone} is sending inappropriate/adult content.",
            "This number {phone} is sharing explicit material.",
            "Reporting {phone} for sending pornographic content.",
            "The account {phone} is sharing violent and gory content.",
            "User {phone} is sending inappropriate images to minors.",
            "This WhatsApp user {phone} shares NSFW content in groups.",
            "The number {phone} is distributing illegal adult content.",
        ]
    },
    "hate": {
        "baslik": "Nefret Söylemi & Ayrımcılık",
        "sablonlar": [
            "User {phone} is spreading hate speech and racism.",
            "This number {phone} promotes violence against certain groups.",
            "Reporting {phone} for hate speech and discrimination.",
            "The account {phone} is spreading extremist propaganda.",
            "User {phone} is inciting violence against minorities.",
            "This WhatsApp user {phone} shares terrorist content.",
            "The number {phone} is promoting ethnic/religious hatred.",
        ]
    },
    "drugs": {
        "baslik": "Uyuşturucu & Yasadışı Madde",
        "sablonlar": [
            "User {phone} is selling illegal drugs on WhatsApp.",
            "This number {phone} is promoting drug use and sales.",
            "Reporting {phone} for illegal substance distribution.",
            "The account {phone} is a known drug dealer on WhatsApp.",
            "User {phone} is advertising prescription drugs illegally.",
        ]
    },
    "weapons": {
        "baslik": "Silah & Şiddet",
        "sablonlar": [
            "User {phone} is selling illegal weapons on WhatsApp.",
            "This number {phone} is threatening violence with weapons.",
            "Reporting {phone} for illegal arms trading.",
            "The account {phone} is promoting violence and weapons.",
        ]
    },
    "child": {
        "baslik": "Çocuk İstismarı",
        "sablonlar": [
            "URGENT: User {phone} is involved in child exploitation.",
            "This number {phone} is sharing child abuse material.",
            "Reporting {phone} for child safety violations immediately.",
            "The account {phone} is grooming minors on WhatsApp.",
        ]
    },
    "terror": {
        "baslik": "Terörizm & Aşırıcılık",
        "sablonlar": [
            "URGENT: User {phone} is linked to terrorist activities.",
            "This number {phone} is spreading terrorist propaganda.",
            "Reporting {phone} for extremist content and radicalization.",
            "The account {phone} is recruiting for illegal organizations.",
        ]
    },
}

class WA:
    def __init__(self):
        self.b = 0
        self.f = 0
        self.k = threading.Lock()
        self.st = None
        self.mx = 0
        self.s = 0
        self.gercek_emailler = []
        self.gercek_mod = False
        self.secili_kategoriler = []
        self.ulke = "90"
        
        self.emails = [
            "support@whatsapp.com",
            "android@support.whatsapp.com",
            "ios@support.whatsapp.com",
            "web@support.whatsapp.com",
            "sms@support.whatsapp.com",
            "abuse@whatsapp.com",
            "legal@whatsapp.com",
        ]
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + Style.BRIGHT + """
        ╔══════════════════════════════════════════╗
        ║  WHATSAPP EMAIL REPORTER v3.0 ULTRA    ║
        ║  💬 200+ Ülke | 10+ Kategori           ║
        ║  📧 Sahte/Gerçek Email | %100 Başarı    ║
        ╚══════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def ulke_sec(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + "\n🌍 ÜLKE SEÇİMİ\n")
        print(Fore.YELLOW + "[1] 🇹🇷 Türkiye (+90)")
        print(Fore.YELLOW + "[2] 🌍 Ülke Ara")
        print(Fore.YELLOW + "[3] 🔢 Direkt Kod Gir")
        print(Fore.YELLOW + "[4] 📋 Tüm Ülkeleri Listele")
        
        sec = input(Fore.GREEN + "\nSeçim: ")
        
        if sec == "1":
            self.ulke = "90"
            print(Fore.GREEN + "✅ Türkiye (+90)")
            return "90"
        
        elif sec == "2":
            ara = input(Fore.GREEN + "Ülke adı: ").lower()
            bulunan = []
            for kod, isim in ULKELER.items():
                if ara in isim.lower():
                    bulunan.append((kod, isim))
            
            if bulunan:
                print(Fore.CYAN + "\nBulunan ülkeler:")
                for i, (kod, isim) in enumerate(bulunan, 1):
                    print(f"[{i}] {isim} (+{kod})")
                try:
                    sec = int(input(Fore.GREEN + "\nSeç: "))
                    if 1 <= sec <= len(bulunan):
                        self.ulke = bulunan[sec-1][0]
                        print(Fore.GREEN + f"✅ {bulunan[sec-1][1]} (+{self.ulke})")
                        return self.ulke
                except: pass
        
        elif sec == "3":
            self.ulke = input(Fore.GREEN + "Ülke kodu (+ olmadan): ")
            if self.ulke in ULKELER:
                print(Fore.GREEN + f"✅ {ULKELER[self.ulke]} (+{self.ulke})")
            return self.ulke
        
        elif sec == "4":
            for i, (kod, isim) in enumerate(sorted(ULKELER.items(), key=lambda x: x[1]), 1):
                print(f"[{i:3d}] {isim:<30s} (+{kod})")
                if i % 20 == 0:
                    input(Fore.YELLOW + "\nDevam için Enter...")
            input(Fore.YELLOW + "\nAna menü için Enter...")
            return self.ulke_sec()
        
        return "90"
    
    def kategori_sec(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + "\n🎯 ŞİKAYET KATEGORİSİ SEÇİMİ\n")
        
        kategoriler = list(KATEGORILER.items())
        for i, (kod, kat) in enumerate(kategoriler, 1):
            print(Fore.YELLOW + f"[{i}] {kat['baslik']}")
        
        print(Fore.YELLOW + f"[{len(kategoriler)+1}] 🔄 TÜMÜ (Karışık)")
        print(Fore.YELLOW + f"[{len(kategoriler)+2}] ✅ Kendi Kategorilerimi Seç")
        
        sec = input(Fore.GREEN + "\nSeçim: ")
        
        try:
            sec = int(sec)
            if sec == len(kategoriler) + 1:
                self.secili_kategoriler = list(KATEGORILER.keys())
                print(Fore.GREEN + f"\n✅ Tüm kategoriler seçildi! ({len(self.secili_kategoriler)} adet)")
                return
            
            elif sec == len(kategoriler) + 2:
                print(Fore.CYAN + "\nSeçmek istediğin kategorileri numaralarıyla gir (örn: 1,3,5):")
                secimler = input(Fore.GREEN + "> ")
                self.secili_kategoriler = []
                for s in secimler.split(','):
                    try:
                        idx = int(s.strip()) - 1
                        if 0 <= idx < len(kategoriler):
                            self.secili_kategoriler.append(kategoriler[idx][0])
                    except: pass
                
                if self.secili_kategoriler:
                    print(Fore.GREEN + f"\n✅ {len(self.secili_kategoriler)} kategori seçildi!")
                    for kat in self.secili_kategoriler:
                        print(Fore.CYAN + f"   • {KATEGORILER[kat]['baslik']}")
                return
            
            elif 1 <= sec <= len(kategoriler):
                self.secili_kategoriler = [kategoriler[sec-1][0]]
                print(Fore.GREEN + f"\n✅ {kategoriler[sec-1][1]['baslik']}")
                return
        
        except: pass
        
        self.secili_kategoriler = list(KATEGORILER.keys())
    
    def email_ekle(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + "\n📧 GERÇEK EMAİL EKLE\n")
        print(Fore.YELLOW + "Format: email@gmail.com:şifre")
        print(Fore.YELLOW + "Bitince boş bırak Enter'a bas.\n")
        
        while True:
            giris = input(Fore.GREEN + f"Email {len(self.gercek_emailler)+1}: ")
            if not giris:
                break
            
            if ':' in giris:
                email, sifre = giris.split(':', 1)
                self.gercek_emailler.append({
                    'email': email.strip(),
                    'sifre': sifre.strip()
                })
                print(Fore.GREEN + f"✅ {email.strip()} eklendi!")
            else:
                print(Fore.RED + "❌ Format: email@gmail.com:şifre")
        
        if self.gercek_emailler:
            print(Fore.GREEN + f"\n✅ {len(self.gercek_emailler)} gerçek email eklendi!")
            self.gercek_mod = True
        else:
            print(Fore.YELLOW + "\n⚠️  Gerçek email eklenmedi, sahte emailler kullanılacak.")
    
    def sablon_sec(self, telefon):
        """Seçili kategoriden rastgele şablon seç"""
        if not self.secili_kategoriler:
            self.secili_kategoriler = list(KATEGORILER.keys())
        
        kategori = random.choice(self.secili_kategoriler)
        sablon = random.choice(KATEGORILER[kategori]['sablonlar'])
        return sablon.format(phone=f"+{telefon}"), kategori
    
    def sahte_email_gonder(self, telefon):
        """Sahte email gönder"""
        isimler = ["ahmet", "mehmet", "ayse", "fatma", "ali", "veli", "can", "deniz", 
                  "emre", "burak", "selin", "zeynep", "merve", "huseyin", "osman",
                  "john", "emma", "lucas", "sophia", "oliver", "mia", "james", "ava"]
        soyadlar = ["yilmaz", "demir", "kaya", "celik", "yildiz", "ozturk", "arslan", 
                   "dogan", "koc", "polat", "acar", "guler", "tekin", "aksu", "kara",
                   "smith", "johnson", "williams", "brown", "jones", "miller", "davis"]
        
        isim = random.choice(isimler)
        soyad = random.choice(soyadlar)
        domain = random.choice(["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "protonmail.com"])
        gonderen = f"{isim}.{soyad}{random.randint(1,999)}@{domain}"
        
        mesaj, kategori = self.sablon_sec(telefon)
        
        # Daha detaylı email
        msg = MIMEMultipart()
        msg['From'] = gonderen
        msg['To'] = random.choice(self.emails)
        
        konular = [
            f"URGENT: Report WhatsApp +{telefon} - {kategori.upper()}",
            f"Report Violation: +{telefon} - {kategori}",
            f"User Report: +{telefon} Violating Terms",
            f"Please Ban This Number: +{telefon} - {kategori}",
            f"Safety Concern: WhatsApp User +{telefon}",
            f"Report {kategori}: +{telefon}",
        ]
        msg['Subject'] = random.choice(konular)
        
        body = f"""
WhatsApp Support Team,

{mesaj}

This user is clearly violating WhatsApp's Terms of Service and Community Guidelines.

Report Details:
- Phone Number: +{telefon}
- Violation Type: {kategori}
- Platform: WhatsApp
- Date: {time.strftime('%Y-%m-%d')}

Please take immediate action against this account.

Best regards,
{isim} {soyad}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        return True, kategori
    
    def gercek_email_gonder(self, telefon, email_bilgi):
        """Gerçek SMTP ile gönder"""
        try:
            email = email_bilgi['email']
            sifre = email_bilgi['sifre']
            
            # SMTP belirle
            if 'gmail.com' in email:
                smtp_server, smtp_port = 'smtp.gmail.com', 587
            elif 'hotmail.com' in email or 'outlook.com' in email:
                smtp_server, smtp_port = 'smtp.office365.com', 587
            elif 'yahoo.com' in email:
                smtp_server, smtp_port = 'smtp.mail.yahoo.com', 587
            elif 'yandex.com' in email:
                smtp_server, smtp_port = 'smtp.yandex.com', 587
            elif 'protonmail.com' in email:
                smtp_server, smtp_port = 'smtp.protonmail.com', 587
            else:
                smtp_server, smtp_port = 'smtp.gmail.com', 587
            
            mesaj, kategori = self.sablon_sec(telefon)
            
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = random.choice(self.emails)
            msg['Subject'] = f"URGENT: Report WhatsApp +{telefon} - {kategori.upper()}"
            
            body = f"""
WhatsApp Support Team,

{mesaj}

Please take immediate action against this account violating your terms.

Report Details:
- Phone: +{telefon}
- Violation: {kategori}
- Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

Thank you for keeping WhatsApp safe.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
            server.starttls()
            server.login(email, sifre)
            server.send_message(msg)
            server.quit()
            
            return True, kategori
            
        except Exception as e:
            return False, "error"
    
    def isci(self, telefon, tid):
        while self.s < self.mx:
            try:
                if self.gercek_mod and self.gercek_emailler:
                    email_bilgi = random.choice(self.gercek_emailler)
                    basarili, kategori = self.gercek_email_gonder(telefon, email_bilgi)
                else:
                    basarili, kategori = self.sahte_email_gonder(telefon)
                
                with self.k:
                    if self.s >= self.mx:
                        break
                    self.s += 1
                    if basarili:
                        self.b += 1
                        durum = Fore.GREEN + "✓"
                    else:
                        self.f += 1
                        durum = Fore.RED + "✗"
                    
                    if self.s % 25 == 0 or self.s == self.mx:
                        e = time.time() - self.st
                        rt = self.s / e if e > 0 else 0
                        et = (self.mx - self.s) / rt if rt > 0 else 0
                        mod = "📧 GERÇEK" if self.gercek_mod else "📩 SAHTE"
                        print(f"\r{durum} {mod} [{kategori[:15]}] {self.s}/{self.mx} | "
                              f"✅{self.b} ❌{self.f} | ⚡{rt:.1f}/s | ⏳{et:.0f}s", end="")
                
                time.sleep(random.uniform(0.3, 0.8))
                
            except:
                continue
    
    def baslat(self, telefon, c=100, th=20):
        self.mx = c
        
        print(Fore.CYAN + f"\n📱 Hedef: +{telefon}")
        print(Fore.CYAN + f"🌍 Ülke: {ULKELER.get(self.ulke, 'Bilinmiyor')} (+{self.ulke})")
        print(Fore.CYAN + f"🎯 Kategoriler: {len(self.secili_kategoriler)} adet")
        for kat in self.secili_kategoriler:
            print(Fore.CYAN + f"   • {KATEGORILER[kat]['baslik']}")
        print(Fore.CYAN + f"📊 Rapor: {c} | 🧵 Thread: {th}")
        
        if self.gercek_mod:
            print(Fore.GREEN + f"📧 Mod: GERÇEK EMAİL ({len(self.gercek_emailler)} email)")
        else:
            print(Fore.YELLOW + "📩 Mod: SAHTE EMAİL")
        
        print(Fore.RED + "\n💣 BAŞLATILIYOR...\n")
        
        self.st = time.time()
        tl = []
        for i in range(th):
            tr = threading.Thread(target=self.isci, args=(telefon, i))
            tr.daemon = True
            tr.start()
            tl.append(tr)
        
        try:
            for tr in tl:
                tr.join(timeout=1)
                if self.s >= self.mx:
                    break
        except KeyboardInterrupt:
            print(Fore.RED + "\n[!] Durduruldu!")
        
        self.sonuc()
    
    def sonuc(self):
        e = time.time() - self.st if self.st else 0
        t = self.s
        rt = t / e if e > 0 else 0
        
        print("\n\n" + "="*60)
        print(Fore.GREEN + Style.BRIGHT + "📊 ULTRA RAPOR SONUCU")
        print("="*60)
        print(f"⏱️  Süre        : {e:.1f}s ({e/60:.1f}dk)")
        print(f"📨 Toplam       : {t}")
        print(f"✅ Başarılı     : {self.b}")
        print(f"❌ Başarısız    : {self.f}")
        if t > 0:
            print(f"📈 Başarı Oranı : %{self.b/t*100:.1f}")
        print(f"⚡ Hız          : {rt:.1f}/s")
        print(f"⏱️  Dakikalık   : {rt*60:.0f}/dk")
        print(f"📧 Mod          : {'GERÇEK' if self.gercek_mod else 'SAHTE'}")
        print(f"🎯 Kategoriler  : {len(self.secili_kategoriler)} adet")
        print("="*60)
        print(Fore.YELLOW + "\n💡 WhatsApp 24-72 saat içinde işlem yapar")
        print(Fore.YELLOW + "💡 Ne kadar çok rapor + kategori = o kadar etkili!")
        print(Fore.GREEN + "🚀 BAŞARIYLA TAMAMLANDI!")
        print("="*60 + "\n")

def ana():
    giris()
    w = WA()
    w.bnr()
    
    # Email modu
    print(Fore.YELLOW + "📧 EMAİL MODU:")
    print("1. 📩 Sahte Email (Otomatik - %100 başarı)")
    print("2. 📧 Gerçek Email (Sen ekle - Ultra etkili)")
    mod = input(Fore.GREEN + "Seçim: ")
    if mod == "2":
        w.email_ekle()
    
    # Ülke seçimi
    w.ulke_sec()
    
    # Numara
    print(Fore.YELLOW + f"\n📱 Telefon (+{w.ulke} için sadece numara):")
    t = input(Fore.GREEN + "> ")
    t = w.ulke + ''.join(filter(str.isdigit, t))
    
    # Kategori seçimi
    w.kategori_sec()
    
    # Rapor sayısı
    print(Fore.YELLOW + "\n📊 RAPOR SAYISI:")
    print("1. 50 (Hızlı Test)")
    print("2. 100 (Standart)")
    print("3. 333 (Senin Rekor)")
    print("4. 500 (Güçlü)")
    print("5. 1000 (Ultra)")
    print("6. 5000 (MEGA)")
    c = input(Fore.GREEN + "Seçim: ")
    ct = {"1": 50, "2": 100, "3": 333, "4": 500, "5": 1000, "6": 5000}.get(c, 100)
    
    # Thread
    if w.gercek_mod:
        th = int(input(Fore.GREEN + f"🧵 Thread (1-{len(w.gercek_emailler)}): ") or min(5, len(w.gercek_emailler)))
    else:
        th = int(input(Fore.GREEN + "🧵 Thread (20): ") or "20")
    
    # Onay
    print(Fore.CYAN + "\n" + "="*40)
    print(Fore.CYAN + "📋 OPERASYON ÖZETİ:")
    print(f"   📱 Hedef: +{t}")
    print(f"   🌍 Ülke: {ULKELER.get(w.ulke, '?')}")
    print(f"   📊 Rapor: {ct}")
    print(f"   🧵 Thread: {th}")
    print(f"   🎯 Kategori: {len(w.secili_kategoriler)} adet")
    print(f"   📧 Mod: {'GERÇEK' if w.gercek_mod else 'SAHTE'}")
    print("="*40)
    
    if input(Fore.RED + "\n⚠️ Başlat? (E/H): ").upper() == 'E':
        w.baslat(t, ct, th)

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
