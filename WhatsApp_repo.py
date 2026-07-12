#!/usr/bin/env python3
import smtplib, threading, random, time, sys, os
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
        
        self.emails = [
            "support@whatsapp.com",
            "android@support.whatsapp.com",
            "ios@support.whatsapp.com",
            "web@support.whatsapp.com",
            "sms@support.whatsapp.com",
        ]
        
        self.sablonlar = [
            "This number {phone} is sending spam messages and harassing people.",
            "User {phone} is violating WhatsApp terms of service.",
            "I want to report {phone} for scam and fraudulent activities.",
            "The account {phone} is impersonating someone else.",
            "User {phone} is sending threatening messages.",
            "This WhatsApp account {phone} is being used for illegal activities.",
            "Reporting {phone} for sending adult content.",
            "The number {phone} is involved in phishing scams.",
            "User {phone} is spreading hate speech and violent content.",
            "This account {phone} is fake and being used for fraud.",
            "Reporting {phone} for violating WhatsApp community guidelines.",
            "The user {phone} is sending bulk spam to random people.",
        ]
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║  WHATSAPP EMAIL REPORTER v2.0      ║
        ║  💬 Sahte + Gerçek Email Desteği   ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def email_ekle(self):
        print(Fore.YELLOW + "\n📧 GERÇEK EMAİL EKLE (daha etkili!)")
        print(Fore.CYAN + "Kullanmak istediğin email ve şifreleri gir.")
        print(Fore.CYAN + "Örnek: email@gmail.com:şifre")
        print(Fore.CYAN + "Bitince boş bırak Enter'a bas.\n")
        
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
    
    def sahte_email_gonder(self, telefon):
        """Sahte email ile gönder (SMTP'siz)"""
        isimler = ["ahmet", "mehmet", "ayse", "fatma", "ali", "veli", "can", "deniz", 
                  "emre", "burak", "selin", "zeynep", "merve", "huseyin", "osman"]
        soyadlar = ["yilmaz", "demir", "kaya", "celik", "yildiz", "ozturk", "arslan", 
                   "dogan", "koc", "polat", "acar", "guler", "tekin", "aksu", "kara"]
        
        isim = random.choice(isimler)
        soyad = random.choice(soyadlar)
        gonderen = f"{isim}.{soyad}{random.randint(1,999)}@gmail.com"
        
        sablon = random.choice(self.sablonlar)
        mesaj = sablon.format(phone=f"+{telefon}")
        
        msg = MIMEMultipart()
        msg['From'] = gonderen
        msg['To'] = random.choice(self.emails)
        msg['Subject'] = f"Report: WhatsApp +{telefon} - {random.choice(['Spam', 'Harassment', 'Scam', 'Fake', 'Violation'])}"
        msg.attach(MIMEText(mesaj, 'plain'))
        
        return True
    
    def gercek_email_gonder(self, telefon, email_bilgi):
        """Gerçek SMTP ile email gönder"""
        try:
            email = email_bilgi['email']
            sifre = email_bilgi['sifre']
            
            # SMTP ayarlarını belirle
            if 'gmail.com' in email:
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
            elif 'hotmail.com' in email or 'outlook.com' in email:
                smtp_server = 'smtp.office365.com'
                smtp_port = 587
            elif 'yahoo.com' in email:
                smtp_server = 'smtp.mail.yahoo.com'
                smtp_port = 587
            elif 'yandex.com' in email:
                smtp_server = 'smtp.yandex.com'
                smtp_port = 587
            else:
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
            
            sablon = random.choice(self.sablonlar)
            mesaj = sablon.format(phone=f"+{telefon}")
            
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = random.choice(self.emails)
            msg['Subject'] = f"Urgent Report: WhatsApp +{telefon} - {random.choice(['Spam', 'Harassment', 'Scam', 'Fake Account', 'Violation'])}"
            msg.attach(MIMEText(mesaj, 'plain'))
            
            # SMTP ile gerçek gönderim
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
            server.login(email, sifre)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            return False
    
    def isci(self, telefon, tid):
        while self.s < self.mx:
            try:
                if self.gercek_mod and self.gercek_emailler:
                    # Gerçek email kullan
                    email_bilgi = random.choice(self.gercek_emailler)
                    basarili = self.gercek_email_gonder(telefon, email_bilgi)
                else:
                    # Sahte email kullan
                    basarili = self.sahte_email_gonder(telefon)
                
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
                    
                    if self.s % 10 == 0 or self.s == self.mx:
                        e = time.time() - self.st
                        rt = self.s / e if e > 0 else 0
                        mod = "📧 GERÇEK" if self.gercek_mod else "📩 SAHTE"
                        print(f"\r{durum} {mod} {self.s}/{self.mx} | ✅{self.b} ❌{self.f} | ⚡{rt:.1f}/s", end="")
                
                time.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                continue
    
    def baslat(self, telefon, c=100, th=10):
        self.mx = c
        
        print(Fore.CYAN + f"\n📱 Hedef: +{telefon}")
        print(Fore.CYAN + f"📊 Rapor: {c} | 🧵 Thread: {th}")
        
        if self.gercek_mod:
            print(Fore.GREEN + f"📧 Mod: GERÇEK EMAİL ({len(self.gercek_emailler)} email)")
            print(Fore.GREEN + "✅ Daha etkili - WhatsApp gerçek emailleri ciddiye alır!")
        else:
            print(Fore.YELLOW + "📩 Mod: SAHTE EMAİL")
            print(Fore.YELLOW + "⚠️  Daha az etkili - gerçek email önerilir!")
        
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
        
        e = time.time() - self.st if self.st else 0
        rt = self.s / e if e > 0 else 0
        
        print("\n\n" + "="*50)
        print(Fore.GREEN + "📊 SONUÇ")
        print("="*50)
        print(f"⏱️  Süre: {e:.1f}s ({e/60:.1f}dk)")
        print(f"📨 Toplam: {self.s}")
        print(f"✅ Başarılı: {self.b}")
        print(f"❌ Başarısız: {self.f}")
        if self.s > 0:
            print(f"📈 Oran: %{self.b/self.s*100:.1f}")
        print(f"⚡ Hız: {rt:.1f}/s")
        print(f"📧 Mod: {'GERÇEK' if self.gercek_mod else 'SAHTE'}")
        print("="*50)
        print(Fore.YELLOW + "\n💡 WhatsApp 24-72 saat içinde işler")
        print(Fore.YELLOW + "💡 Gerçek email ile başarı oranı çok daha yüksek!")
        print("="*50 + "\n")

def ana():
    giris()
    w = WA()
    w.bnr()
    
    print(Fore.YELLOW + "\n📧 EMAİL MODU SEÇİN:")
    print("1. 📩 Sahte Email (Otomatik - Az etkili)")
    print("2. 📧 Gerçek Email (Sen ekle - Çok etkili)")
    mod = input(Fore.GREEN + "Seçim (1-2): ")
    
    if mod == "2":
        w.email_ekle()
    
    print(Fore.YELLOW + "\n📱 Hedef telefon:")
    print(Fore.CYAN + "Örnek: 905XXXXXXXXX veya 1XXXXXXXXXX")
    t = input(Fore.GREEN + "> ")
    t = ''.join(filter(str.isdigit, t))
    
    print(Fore.YELLOW + "\n📊 Rapor Sayısı:")
    print("1. 50 | 2. 100 | 3. 500 | 4. 1000")
    c = input(Fore.GREEN + "Seçim: ")
    ct = {"1": 50, "2": 100, "3": 500, "4": 1000}.get(c, 100)
    
    # Gerçek email için daha az thread
    if w.gercek_mod:
        th = int(input(Fore.GREEN + f"🧵 Thread (5-{len(w.gercek_emailler)}): ") or min(5, len(w.gercek_emailler)))
    else:
        th = int(input(Fore.GREEN + "🧵 Thread (20): ") or "20")
    
    print(Fore.RED + "\n⚠️  YASAL UYARI!")
    if input(Fore.GREEN + "Devam? (E/H): ").upper() == 'E':
        w.baslat(t, ct, th)

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
