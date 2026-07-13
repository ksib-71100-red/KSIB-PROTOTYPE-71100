#!/usr/bin/env python3
# KSIB CC GENERATOR v3.0 PRO - Profesyonel Arayüz | Gerçekçi Veriler
import random, sys, os, json, time, datetime
from colorama import init, Fore, Back, Style
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════╗
    ║        🔐 KSIB PRO GİRİŞ           ║
    ╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    for i in range(3):
        s = input(Fore.YELLOW + "\n🔑 Şifre: ")
        if s == SIFRE:
            print(Fore.GREEN + "\n✅ Giriş başarılı! Yükleniyor...\n")
            time.sleep(1)
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    sys.exit(0)

class CCGeneratorPro:
    def __init__(self):
        # BANKALAR ve BIN kodları
        self.bankalar = {
            "🇹🇷 Türkiye": {
                "Garanti BBVA": {"visa": "428220", "mastercard": "542429", "amex": "375670"},
                "İş Bankası": {"visa": "454314", "mastercard": "548819", "amex": "375671"},
                "Akbank": {"visa": "435508", "mastercard": "512754", "amex": "375672"},
                "Yapı Kredi": {"visa": "492024", "mastercard": "539611", "amex": "375673"},
                "Ziraat Bankası": {"visa": "454671", "mastercard": "540134", "amex": "375674"},
                "Halkbank": {"visa": "492130", "mastercard": "540061", "amex": "375675"},
                "Vakıfbank": {"visa": "409312", "mastercard": "542029", "amex": "375676"},
                "Denizbank": {"visa": "409364", "mastercard": "520019", "amex": "375677"},
                "QNB Finansbank": {"visa": "402277", "mastercard": "521394", "amex": "375678"},
                "TEB": {"visa": "440293", "mastercard": "534563", "amex": "375679"},
                "ING Bank": {"visa": "420109", "mastercard": "554960", "amex": "375680"},
                "Kuveyt Türk": {"visa": "402940", "mastercard": "536055", "amex": "375681"},
                "Albaraka Türk": {"visa": "434727", "mastercard": "533596", "amex": "375682"},
                "Enpara": {"visa": "440274", "mastercard": "549400", "amex": "375683"},
                "Papara": {"visa": "428945", "mastercard": "539600", "amex": "375684"},
            },
            "🇺🇸 ABD": {
                "Chase": {"visa": "414720", "mastercard": "524040", "amex": "375685"},
                "Bank of America": {"visa": "480011", "mastercard": "546616", "amex": "375686"},
                "Wells Fargo": {"visa": "486236", "mastercard": "518219", "amex": "375687"},
                "Citibank": {"visa": "412800", "mastercard": "542418", "amex": "375688"},
                "Capital One": {"visa": "476134", "mastercard": "517805", "amex": "375689"},
                "American Express": {"visa": "370000", "mastercard": "370001", "amex": "370002"},
            },
            "🇬🇧 İngiltere": {
                "HSBC": {"visa": "465865", "mastercard": "540168", "amex": "375690"},
                "Barclays": {"visa": "492181", "mastercard": "530133", "amex": "375691"},
                "Lloyds": {"visa": "476367", "mastercard": "545460", "amex": "375692"},
                "NatWest": {"visa": "453979", "mastercard": "557347", "amex": "375693"},
            },
            "🇩🇪 Almanya": {
                "Deutsche Bank": {"visa": "492940", "mastercard": "520645", "amex": "375694"},
                "Commerzbank": {"visa": "453010", "mastercard": "541557", "amex": "375695"},
                "N26": {"visa": "476149", "mastercard": "535456", "amex": "375696"},
            },
            "🇷🇺 Rusya": {
                "Sberbank": {"visa": "427601", "mastercard": "546938", "amex": "375697"},
                "VTB": {"visa": "462729", "mastercard": "527576", "amex": "375698"},
                "Tinkoff": {"visa": "437773", "mastercard": "518901", "amex": "375699"},
            },
        }
        
        # İSİM VERİTABANI
        self.isimler = {
            "TR": {
                "erkek": ["Ahmet", "Mehmet", "Mustafa", "Ali", "Hüseyin", "İbrahim", "Osman", "Yusuf", 
                         "Emre", "Burak", "Can", "Deniz", "Kemal", "Murat", "Ömer", "Serkan", "Tolga",
                         "Umut", "Volkan", "Yasin", "Zafer", "Berk", "Cem", "Doruk", "Ege", "Fırat",
                         "Gökhan", "Hakan", "İlker", "Kaan", "Levent", "Mert", "Onur", "Polat"],
                "kadin": ["Ayşe", "Fatma", "Emine", "Zeynep", "Elif", "Merve", "Büşra", "Selin",
                         "Aslı", "Berna", "Ceren", "Derya", "Eda", "Funda", "Gamze", "Hande",
                         "İrem", "Jale", "Kübra", "Lale", "Melis", "Nazlı", "Özge", "Pınar"]
            },
            "US": {
                "erkek": ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
                         "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
                         "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian"],
                "kadin": ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
                         "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
                         "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol"]
            },
            "UK": {
                "erkek": ["Oliver", "Jack", "Harry", "George", "Jacob", "Charlie", "Thomas", "James",
                         "William", "Henry", "Samuel", "Daniel", "Benjamin", "Alexander", "Ethan"],
                "kadin": ["Amelia", "Olivia", "Emily", "Isla", "Ava", "Jessica", "Isabella", "Sophie",
                         "Mia", "Ruby", "Lily", "Grace", "Evie", "Charlotte", "Ella"]
            },
            "DE": {
                "erkek": ["Lukas", "Leon", "Luca", "Paul", "Jonas", "Felix", "Maximilian", "David",
                         "Tim", "Niklas", "Tom", "Jan", "Philipp", "Erik", "Fabian"],
                "kadin": ["Mia", "Emma", "Hannah", "Sofia", "Anna", "Lina", "Lea", "Marie",
                         "Lena", "Emily", "Laura", "Julia", "Lisa", "Sarah", "Maja"]
            },
        }
        
        self.soyadlar = {
            "TR": ["YILMAZ", "DEMİR", "KAYA", "ÇELİK", "ŞAHİN", "YILDIZ", "ÖZTÜRK", "ARSLAN",
                   "DOĞAN", "KILIÇ", "ASLAN", "ÇETİN", "KARA", "KOÇ", "POLAT", "AKSOY",
                   "TÜRK", "GÜLER", "AYDIN", "BULUT", "ÖZDEMİR", "ACAR", "TEKİN", "KORKMAZ"],
            "US": ["SMITH", "JOHNSON", "WILLIAMS", "BROWN", "JONES", "GARCIA", "MILLER", "DAVIS",
                   "RODRIGUEZ", "MARTINEZ", "HERNANDEZ", "LOPEZ", "GONZALEZ", "WILSON", "ANDERSON",
                   "THOMAS", "TAYLOR", "MOORE", "JACKSON", "MARTIN", "LEE", "PEREZ", "THOMPSON"],
            "UK": ["SMITH", "JONES", "WILLIAMS", "TAYLOR", "BROWN", "DAVIES", "EVANS", "WILSON",
                   "THOMAS", "ROBERTS", "JOHNSON", "LEWIS", "WALKER", "ROBINSON", "WOOD"],
            "DE": ["MÜLLER", "SCHMIDT", "SCHNEIDER", "FISCHER", "WEBER", "MEYER", "WAGNER", "BECKER",
                   "HOFFMANN", "SCHÄFER", "KOCH", "BAUER", "RICHTER", "KLEIN", "WOLF"],
        }
        
        self.sehirler = {
            "TR": ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep"],
            "US": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego"],
            "UK": ["London", "Manchester", "Birmingham", "Liverpool", "Edinburgh", "Glasgow", "Bristol", "Leeds"],
            "DE": ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf", "Leipzig"],
        }
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════════════════╗
        ║  💳  KSIB CC GENERATOR v3.0 PRO ULTRA         ║
        ║  🏦 Gerçek BIN | 👤 Gerçekçi İsim             ║
        ║  🌍 5 Ülke | 30+ Banka | Luhn Doğrulama       ║
        ║  📊 CSV/JSON Export | Profesyonel Arayüz       ║
        ╚══════════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def luhn_generate(self, prefix, length=16):
        """Luhn algoritması ile geçerli kart üret"""
        card = list(str(prefix))
        while len(card) < length - 1:
            card.append(str(random.randint(0, 9)))
        
        # Luhn kontrol basamağı
        digits = [int(d) for d in card]
        for i in range(len(digits) - 1, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        total = sum(digits)
        check = (10 - (total % 10)) % 10
        card.append(str(check))
        
        return ''.join(card)
    
    def luhn_check(self, card_num):
        """Luhn doğrulama"""
        digits = [int(d) for d in str(card_num)]
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10 == 0
    
    def format_card(self, number, card_type):
        """Kartı formatla"""
        number = str(number)
        if card_type == "Amex":
            return f"{number[:4]} {number[4:10]} {number[10:]}"
        else:
            return ' '.join([number[i:i+4] for i in range(0, 16, 4)])
    
    def generate_cvv(self, card_type):
        """CVV üret"""
        return str(random.randint(1000, 9999)) if card_type == "Amex" else str(random.randint(100, 999))
    
    def generate_expiry(self):
        """Son kullanma tarihi"""
        month = random.randint(1, 12)
        year = random.randint(2025, 2029)
        return f"{month:02d}/{year}"
    
    def generate_name(self, country_code):
        """Ülkeye uygun isim soyisim"""
        if country_code not in self.isimler:
            country_code = "US"
        
        cinsiyet = random.choice(["erkek", "kadin"])
        isim = random.choice(self.isimler[country_code][cinsiyet])
        soyad = random.choice(self.soyadlar.get(country_code, self.soyadlar["US"]))
        
        return f"{isim} {soyad}".upper()
    
    def generate_card_details(self, ulke_kodu, banka_adi, kart_tipi):
        """Tam kart detayı üret"""
        # BIN al
        banka = self.bankalar[ulke_kodu][banka_adi]
        bin_prefix = banka[kart_tipi.lower()]
        
        # Kart numarası
        length = 15 if kart_tipi == "Amex" else 16
        card_number = self.luhn_generate(bin_prefix, length)
        
        # Diğer bilgiler
        expiry = self.generate_expiry()
        cvv = self.generate_cvv(kart_tipi)
        isim = self.generate_name(ulke_kodu.split()[1] if " " in ulke_kodu else "US")
        
        # Ülke kodu çıkar
        country_code = ulke_kodu.split()[1] if " " in ulke_kodu else "TR"
        sehir = random.choice(self.sehirler.get(country_code, ["Unknown"]))
        
        return {
            "kart_no": card_number,
            "kart_format": self.format_card(card_number, kart_tipi),
            "son_kullanim": expiry,
            "cvv": cvv,
            "isim": isim,
            "banka": banka_adi,
            "kart_tipi": kart_tipi,
            "ulke": ulke_kodu,
            "sehir": sehir,
            "luhn": self.luhn_check(card_number),
            "bin": bin_prefix,
            "uretim_tarihi": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def export_json(self, cards, filename=None):
        if not filename:
            filename = f"cc_cards_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)
        print(Fore.GREEN + f"\n💾 JSON: {filename}")
        return filename
    
    def export_csv(self, cards, filename=None):
        if not filename:
            filename = f"cc_cards_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Kart No,Son Kullanma,CVV,İsim,Banka,Tip,Ülke,Şehir,Luhn,BIN\n")
            for c in cards:
                f.write(f"{c['kart_no']},{c['son_kullanim']},{c['cvv']},{c['isim']},"
                       f"{c['banka']},{c['kart_tipi']},{c['ulke']},{c['sehir']},"
                       f"{c['luhn']},{c['bin']}\n")
        print(Fore.GREEN + f"💾 CSV: {filename}")
        return filename

def menu_ulke():
    print(Fore.YELLOW + "\n🌍 ÜLKE SEÇİN:")
    print(Fore.CYAN + "1. 🇹🇷 Türkiye (15 Banka)")
    print(Fore.CYAN + "2. 🇺🇸 ABD (6 Banka)")
    print(Fore.CYAN + "3. 🇬🇧 İngiltere (4 Banka)")
    print(Fore.CYAN + "4. 🇩🇪 Almanya (3 Banka)")
    print(Fore.CYAN + "5. 🇷🇺 Rusya (3 Banka)")
    print(Fore.CYAN + "6. 🎲 Tüm Ülkeler Karışık")
    return input(Fore.GREEN + "\nSeçim (1-6): ")

def menu_banka(cc, ulke_adi):
    print(Fore.YELLOW + f"\n🏦 {ulke_adi} BANKALARI:")
    bankalar = list(cc.bankalar[ulke_adi].keys())
    for i, banka in enumerate(bankalar, 1):
        print(Fore.CYAN + f"{i}. {banka}")
    print(Fore.CYAN + f"{len(bankalar)+1}. 🎲 Rastgele Banka")
    
    sec = int(input(Fore.GREEN + f"\nSeçim (1-{len(bankalar)+1}): "))
    if sec == len(bankalar) + 1:
        return random.choice(bankalar)
    return bankalar[sec-1]

def menu_kart_tipi():
    print(Fore.YELLOW + "\n💳 KART TİPİ:")
    print(Fore.CYAN + "1. 💙 Visa")
    print(Fore.CYAN + "2. 🧡 Mastercard")
    print(Fore.CYAN + "3. 💎 Amex")
    print(Fore.CYAN + "4. 🎲 Rastgele")
    sec = input(Fore.GREEN + "\nSeçim (1-4): ")
    return {"1": "Visa", "2": "Mastercard", "3": "Amex", "4": "random"}.get(sec, "Visa")

def kart_goster(kart, index):
    """Profesyonel kart görünümü"""
    luhn_icon = Fore.GREEN + "✅" if kart['luhn'] else Fore.RED + "❌"
    
    print(Fore.WHITE + f"""
    ╔══════════════════════════════════════════════╗
    ║  💳 KART #{index}                                  ║
    ╠══════════════════════════════════════════════╣
    ║  🏦 Banka: {kart['banka']:<32s} ║
    ║  💳 Tip  : {kart['kart_tipi']:<32s} ║
    ║  🌍 Ülke : {kart['ulke']:<32s} ║
    ║  📍 Şehir: {kart['sehir']:<32s} ║
    ║  👤 İsim : {kart['isim']:<32s} ║
    ║                                           ║
    ║  🔢 {kart['kart_format']:<38s} ║
    ║                                           ║
    ║  📅 SKT: {kart['son_kullanim']}   🔐 CVV: {kart['cvv']}   {luhn_icon} LUHN ║
    ║  🔍 BIN: {kart['bin']}                          ║
    ╚══════════════════════════════════════════════╝
    """)

def ana():
    giris()
    cc = CCGeneratorPro()
    cc.bnr()
    
    # Ülke seçimi
    ulke_sec = menu_ulke()
    ulke_kodlari = {
        "1": "🇹🇷 Türkiye", "2": "🇺🇸 ABD", "3": "🇬🇧 İngiltere",
        "4": "🇩🇪 Almanya", "5": "🇷🇺 Rusya", "6": "random"
    }
    ulke_adi = ulke_kodlari.get(ulke_sec, "🇹🇷 Türkiye")
    
    # Kart tipi
    kart_tipi = menu_kart_tipi()
    
    # Adet
    print(Fore.YELLOW + "\n📊 KAÇ KART ÜRETİLSİN?")
    print(Fore.CYAN + "1. 1 Kart (Test)")
    print(Fore.CYAN + "2. 5 Kart")
    print(Fore.CYAN + "3. 10 Kart")
    print(Fore.CYAN + "4. 25 Kart")
    print(Fore.CYAN + "5. 50 Kart")
    print(Fore.CYAN + "6. 100 Kart")
    print(Fore.CYAN + "7. Özel Sayı")
    
    adet_sec = input(Fore.GREEN + "\nSeçim: ")
    adet_map = {"1": 1, "2": 5, "3": 10, "4": 25, "5": 50, "6": 100}
    adet = adet_map.get(adet_sec, 10)
    if adet_sec == "7":
        adet = int(input(Fore.GREEN + "Adet: "))
        adet = min(adet, 1000)
    
    # ÜRETİM
    print(Fore.YELLOW + f"\n⚡ {adet} KART ÜRETİLİYOR...\n")
    time.sleep(0.5)
    
    kartlar = []
    ulkeler_list = list(cc.bankalar.keys())
    
    for i in range(1, adet + 1):
        # Ülke seç
        if ulke_adi == "random":
            ulke = random.choice(ulkeler_list)
        else:
            ulke = ulke_adi
        
        # Banka seç
        banka = random.choice(list(cc.bankalar[ulke].keys()))
        
        # Kart tipi
        if kart_tipi == "random":
            tip = random.choice(["Visa", "Mastercard", "Amex"])
        else:
            tip = kart_tipi
        
        # Kart üret
        kart = cc.generate_card_details(ulke, banka, tip)
        kartlar.append(kart)
        
        # Göster
        kart_goster(kart, i)
        
        if i < adet:
            time.sleep(0.2)
    
    # İSTATİSTİK
    print(Fore.YELLOW + "\n" + "="*50)
    print(Fore.CYAN + Style.BRIGHT + "📊 ÜRETİM RAPORU")
    print(Fore.YELLOW + "="*50)
    print(Fore.WHITE + f"📦 Toplam Kart: {len(kartlar)}")
    
    luhn_ok = sum(1 for k in kartlar if k['luhn'])
    print(Fore.GREEN + f"✅ Luhn Geçerli: {luhn_ok}")
    print(Fore.RED + f"❌ Luhn Geçersiz: {len(kartlar) - luhn_ok}")
    
    # Kart tipi dağılımı
    from collections import Counter
    tipler = Counter(k['kart_tipi'] for k in kartlar)
    print(Fore.CYAN + "\n💳 Kart Tipi Dağılımı:")
    for tip, sayi in tipler.items():
        print(Fore.WHITE + f"   {tip}: {sayi} adet")
    
    # Ülke dağılımı
    ulkeler_say = Counter(k['ulke'] for k in kartlar)
    print(Fore.CYAN + "\n🌍 Ülke Dağılımı:")
    for ulke, sayi in ulkeler_say.items():
        print(Fore.WHITE + f"   {ulke}: {sayi} adet")
    
    print(Fore.YELLOW + "="*50)
    
    # KAYDET
    print(Fore.YELLOW + "\n💾 DIŞA AKTAR:")
    print(Fore.CYAN + "1. JSON olarak kaydet")
    print(Fore.CYAN + "2. CSV olarak kaydet")
    print(Fore.CYAN + "3. Her ikisi de")
    print(Fore.CYAN + "4. Kaydetme")
    
    kaydet = input(Fore.GREEN + "\nSeçim: ")
    
    if kaydet == "1":
        cc.export_json(kartlar)
    elif kaydet == "2":
        cc.export_csv(kartlar)
    elif kaydet == "3":
        cc.export_json(kartlar)
        cc.export_csv(kartlar)
    
    # TEKRAR
    print(Fore.YELLOW + "\n🔄 Tekrar üretmek ister misin?")
    tekrar = input(Fore.GREEN + "(E/H): ")
    if tekrar.upper() == 'E':
        ana()
    else:
        print(Fore.GREEN + "\n👋 Görüşürüz!")
        print(Fore.RED + "⚠️  BU KARTLAR GERÇEK DEĞİLDİR! SADECE TEST AMAÇLIDIR!")

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Program kapatıldı!")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n[!] Hata: {e}")
        sys.exit(1)
