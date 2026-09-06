#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
numara_cozum.py
Numara Çözüm Tool'u v6.2

Kurulum:
    pip install requests phonenumbers twilio flask reportlab python-dotenv

Opsiyonel .env:
    NUMVERIFY_API_KEY=
    TRUE_CALLER_API_KEY=
    TWILIO_ACCOUNT_SID=
    TWILIO_AUTH_TOKEN=
    TELEGRAM_BOT_TOKEN=
    TELEGRAM_CHAT_ID=
    META_ACCESS_TOKEN=
    PHONE_NUMBER_ID=
    WABA_ID=
    WHATSAPP_API_VERSION=
    FLASK_SECRET_KEY=
"""

import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import phonenumbers
from dotenv import load_dotenv
from phonenumbers import carrier, geocoder, PhoneNumberType


# ============================================================
# AYARLAR
# ============================================================

load_dotenv()

APP_NAME = "Numara Çözüm Tool'u"
APP_VERSION = "6.2"

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "raporlar"

DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


def env(name, default=""):
    return os.getenv(name, default).strip()


NUMVERIFY_API_KEY = env("NUMVERIFY_API_KEY")
TRUE_CALLER_API_KEY = env("TRUE_CALLER_API_KEY")

TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")

# Meta Graph API
META_ACCESS_TOKEN = env("META_ACCESS_TOKEN") or env("FACEBOOK_ACCESS_TOKEN")
PHONE_NUMBER_ID = env("PHONE_NUMBER_ID")
WABA_ID = env("WABA_ID")

# API sürümünü sabit olarak "güncel" kabul etmiyoruz.
WHATSAPP_API_VERSION = env("WHATSAPP_API_VERSION")

FLASK_SECRET_KEY = env("FLASK_SECRET_KEY", "change-this-secret-key")


# ============================================================
# ENDPOINTLER
# ============================================================

TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"
TWILIO_MESSAGING_API = "https://messaging.twilio.com/v1"
TWILIO_VERIFY_API = "https://verify.twilio.com/v2"
TWILIO_LOOKUP_API = "https://lookups.twilio.com/v2"
TWILIO_CONVERSATIONS_API = "https://conversations.twilio.com/v1"
TWILIO_TASKROUTER_API = "https://taskrouter.twilio.com/v1"
TWILIO_STUDIO_API = "https://studio.twilio.com/v2"
TWILIO_FLEX_API = "https://flex-api.twilio.com/v1"
TWILIO_TRUNKING_API = "https://trunking.twilio.com/v1"

WHATSAPP_GRAPH_API = "https://graph.facebook.com"


# ============================================================
# RENKLER
# ============================================================

R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
M = "\033[95m"
C = "\033[96m"
W = "\033[97m"
N = "\033[0m"
BOLD = "\033[1m"


# ============================================================
# DOSYALAR
# ============================================================

KARA_LISTE_DOSYASI = DATA_DIR / "kara_liste.json"
TELEFON_DEFTERI_DOSYASI = DATA_DIR / "telefon_defteri.json"
TWILIO_NUMARALAR_DOSYASI = DATA_DIR / "twilio_numaralar.json"

KARA_LISTE = []
TELEFON_DEFTERI = []


# ============================================================
# JSON YARDIMCILARI
# ============================================================

def json_yukle(dosya, varsayilan):
    try:
        if not dosya.exists():
            return varsayilan

        with open(dosya, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    except (OSError, json.JSONDecodeError):
        return varsayilan


def json_kaydet(dosya, data):
    try:
        with open(dosya, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )
        return True

    except OSError as e:
        print(f"  ❌ Dosya yazma hatası: {e}")
        return False


def kara_liste_yukle():
    global KARA_LISTE
    data = json_yukle(KARA_LISTE_DOSYASI, [])

    if isinstance(data, list):
        KARA_LISTE = data
    else:
        KARA_LISTE = []


def kara_liste_kaydet():
    return json_kaydet(KARA_LISTE_DOSYASI, KARA_LISTE)


def defter_yukle():
    global TELEFON_DEFTERI
    data = json_yukle(TELEFON_DEFTERI_DOSYASI, [])

    if isinstance(data, list):
        TELEFON_DEFTERI = data
    else:
        TELEFON_DEFTERI = []


def defter_kaydet():
    return json_kaydet(TELEFON_DEFTERI_DOSYASI, TELEFON_DEFTERI)


kara_liste_yukle()
defter_yukle()


# ============================================================
# GENEL YARDIMCILAR
# ============================================================

def temizle():
    os.system("clear" if os.name != "nt" else "cls")


def bekle():
    input("\nDevam etmek için ENTER'a bas...")


def safe_int_input(prompt, default=0, minimum=None, maximum=None):
    try:
        value = input(prompt).strip()

        if not value:
            return default

        number = int(value)

        if minimum is not None and number < minimum:
            return default

        if maximum is not None and number > maximum:
            return default

        return number

    except ValueError:
        return default


def sadece_rakamlar(value):
    return re.sub(r"\D", "", value or "")


# ============================================================
# NUMARA SORGULA
# ============================================================

class NumaraSorgula:

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "NumaraCozum/6.2 "
                "(Python requests)"
            )
        })

        self.sorgu_gecmisi = []
        self.wa = None

    # --------------------------------------------------------
    # NUMARA TEMİZLE
    # --------------------------------------------------------

    def temizle(self, numara):
        return sadece_rakamlar(numara)

    # --------------------------------------------------------
    # PHONENUMBERS PARSE
    # --------------------------------------------------------

    def parse(self, numara, default_region="TR"):
        try:
            text = str(numara).strip()

            if not text:
                return None

            # + ile başlıyorsa uluslararası parse
            if text.startswith("+"):
                return phonenumbers.parse(text, None)

            # Türkiye varsayılan bölge
            return phonenumbers.parse(text, default_region)

        except phonenumbers.NumberParseException:
            return None

    # --------------------------------------------------------
    # FORMAT
    # --------------------------------------------------------

    def formatla(self, numara):
        parsed = self.parse(numara)

        if not parsed:
            return None

        try:
            if not phonenumbers.is_possible_number(parsed):
                return None

            if not phonenumbers.is_valid_number(parsed):
                return None

            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )

        except Exception:
            return None

    # --------------------------------------------------------
    # ÜLKE
    # --------------------------------------------------------

    def ulke_bul(self, numara):
        parsed = self.parse(numara)

        if not parsed:
            return None

        try:
            return {
                "kod": parsed.country_code,
                "adi": geocoder.country_name_for_number(
                    parsed,
                    "tr"
                ) or "Bilinmiyor"
            }

        except Exception:
            return None

    # --------------------------------------------------------
    # OPERATÖR
    # --------------------------------------------------------

    def operator_bul(self, numara):
        parsed = self.parse(numara)

        if not parsed:
            return "Bilinmiyor"

        try:
            result = carrier.name_for_number(
                parsed,
                "tr"
            )

            if result:
                return result

            return "Bilinmiyor"

        except Exception:
            return "Bilinmiyor"

    # --------------------------------------------------------
    # NUMARA TİPİ
    # --------------------------------------------------------

    def tip_bul(self, numara):
        parsed = self.parse(numara)

        if not parsed:
            return "Bilinmiyor"

        try:
            tip = phonenumbers.number_type(parsed)

            tipler = {
                PhoneNumberType.FIXED_LINE: "Sabit Hat",
                PhoneNumberType.MOBILE: "Cep Telefonu",
                PhoneNumberType.FIXED_LINE_OR_MOBILE: "Sabit/Cep",
                PhoneNumberType.TOLL_FREE: "Ücretsiz",
                PhoneNumberType.PREMIUM_RATE: "Premium",
                PhoneNumberType.SHARED_COST: "Paylaşımlı",
                PhoneNumberType.VOIP: "VoIP",
                PhoneNumberType.PERSONAL_NUMBER: "Kişisel",
                PhoneNumberType.PAGER: "Çağrı Cihazı",
                PhoneNumberType.UAN: "UAN",
                PhoneNumberType.VOICEMAIL: "Sesli Mesaj",
                PhoneNumberType.UNKNOWN: "Bilinmiyor",
            }

            return tipler.get(tip, "Bilinmiyor")

        except Exception:
            return "Bilinmiyor"

    # --------------------------------------------------------
    # GEÇERLİLİK
    # --------------------------------------------------------

    def gecerli_mi(self, numara):
        parsed = self.parse(numara)

        if not parsed:
            return False

        try:
            return phonenumbers.is_valid_number(parsed)

        except Exception:
            return False

    # --------------------------------------------------------
    # MÜMKÜN MÜ?
    # --------------------------------------------------------

    def mumkun_mu(self, numara):
        parsed = self.parse(numara)

        if not parsed:
            return False

        try:
            return phonenumbers.is_possible_number(parsed)

        except Exception:
            return False

    # --------------------------------------------------------
    # KONUM
    # --------------------------------------------------------

    def konum_bul(self, numara):
        parsed = self.parse(numara)

        if not parsed:
            return "Bilinmiyor"

        try:
            result = geocoder.description_for_number(
                parsed,
                "tr"
            )

            return result or "Bilinmiyor"

        except Exception:
            return "Bilinmiyor"

    # --------------------------------------------------------
    # ZAMAN DİLİMİ
    # --------------------------------------------------------

    def zaman_dilimi_bul(self, numara):
        parsed = self.parse(numara)

        if not parsed:
            return []

        try:
            return list(
                phonenumbers.time_zones_for_number(parsed)
            )

        except Exception:
            return []

    # --------------------------------------------------------
    # WHATSAPP
    # --------------------------------------------------------

    def whatsapp_kontrol(self, numara):
        """
        Meta Cloud API üzerinden genel olarak
        'bu numara WhatsApp'ta kayıtlı mı?' sorgusu yapmaz.

        Bu nedenle burada sahte True/False üretmiyoruz.

        None:
            Kontrol edilemez / desteklenmiyor.
        """

        return None

    # --------------------------------------------------------
    # TRUECALLER
    # --------------------------------------------------------

    def truecaller_spam_kontrol(self, numara):
        """
        Doğrulanmamış/fake Truecaller endpoint'i kullanmıyoruz.

        Yerel kara liste kontrolü yapılabilir.
        """

        temiz = self.temizle(numara)

        eslesmeler = [
            n for n in KARA_LISTE
            if self.temizle(n) == temiz
        ]

        if eslesmeler:
            return {
                "spam": True,
                "rapor": len(eslesmeler),
                "skor": 85,
                "kaynak": "Yerel Kara Liste"
            }

        return {
            "spam": False,
            "rapor": 0,
            "skor": 0,
            "kaynak": "Yerel Kara Liste"
        }

    # --------------------------------------------------------
    # NUMVERIFY
    # --------------------------------------------------------

    def numverify_dogrula(self, numara):

        if not NUMVERIFY_API_KEY:
            return {
                "hata": (
                    "NUMVERIFY_API_KEY ayarlanmamış."
                )
            }

        try:
            response = self.session.get(
                "https://apilayer.net/api/validate",
                params={
                    "access_key": NUMVERIFY_API_KEY,
                    "number": numara
                },
                timeout=10
            )

            if response.ok:
                return response.json()

            return {
                "hata": f"HTTP {response.status_code}",
                "detay": response.text[:500]
            }

        except requests.RequestException as e:
            return {
                "hata": f"Bağlantı hatası: {e}"
            }

    # --------------------------------------------------------
    # TELEGRAM
    # --------------------------------------------------------

    def telegram_bot_sorgu(self, numara):

        if not TELEGRAM_BOT_TOKEN:
            return {
                "success": False,
                "hata": "TELEGRAM_BOT_TOKEN ayarlanmamış."
            }

        if not TELEGRAM_CHAT_ID:
            return {
                "success": False,
                "hata": "TELEGRAM_CHAT_ID ayarlanmamış."
            }

        try:
            response = self.session.post(
                f"https://api.telegram.org/bot"
                f"{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": (
                        f"📱 Numara sorgusu: {numara}\n"
                        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                },
                timeout=10
            )

            if response.ok:
                return {
                    "success": True,
                    "message": "Telegram'a gönderildi"
                }

            return {
                "success": False,
                "hata": f"HTTP {response.status_code}",
                "detay": response.text[:500]
            }

        except requests.RequestException as e:
            return {
                "success": False,
                "hata": str(e)
            }

    # --------------------------------------------------------
    # NUMARA TAHMİN
    # --------------------------------------------------------

    def numara_tahmin(self, prefix, adet=10):

        prefix = sadece_rakamlar(prefix)

        if not prefix:
            print("  ❌ Prefix boş olamaz.")
            return []

        if len(prefix) >= 10:
            print("  ❌ Prefix çok uzun.")
            return []

        adet = max(1, min(adet, 100))

        print(f"\n{BOLD}{C}🔮 NUMARA TAHMİN{N}")
        print("=" * 50)
        print(f"  Prefix: {prefix}")
        print(f"  Adet: {adet}")
        print("  ⚠️ Bunlar gerçek kişilere ait olduğu garanti olmayan")
        print("     rastgele oluşturulmuş numaralardır.")
        print("=" * 50)

        kalan_hane = 10 - len(prefix)
        sonuclar = []

        for i in range(adet):
            son = "".join(
                str(random.randint(0, 9))
                for _ in range(kalan_hane)
            )

            num = f"+90{prefix}{son}"
            sonuclar.append(num)

            print(f"  {i + 1}. {num}")

        print("=" * 50)

        return sonuclar

    # --------------------------------------------------------
    # IP
    # --------------------------------------------------------

    def ip_bul(self, numara):
        print(f"\n{BOLD}{Y}🌐 IP ADRESİ{N}")
        print("=" * 50)
        print(f"  📞 Numara: {numara}")
        print()
        print("  ❌ Bir telefon numarasından IP adresi")
        print("     bu şekilde tespit edilemez.")
        print("=" * 50)

    # --------------------------------------------------------
    # NUMARA ÜRET
    # --------------------------------------------------------

    def numara_uret(self, ulke="TR"):

        ulke = ulke.upper()

        if ulke == "TR":

            prefix = random.choice([
                "0530", "0531", "0532", "0533",
                "0534", "0535", "0536", "0537",
                "0538", "0539", "0541", "0542",
                "0543", "0544", "0545", "0546",
                "0547", "0548", "0549", "0551",
                "0552", "0553", "0554", "0555",
                "0556", "0557", "0558", "0559"
            ])

            son = "".join(
                str(random.randint(0, 9))
                for _ in range(7)
            )

            return f"+90{prefix[1:]}{son}"

        if ulke == "US":
            return "+1" + "".join(
                str(random.randint(0, 9))
                for _ in range(10)
            )

        return None

    # --------------------------------------------------------
    # TOPLU ANALİZ
    # --------------------------------------------------------

    def toplu_analiz(self, dosya):

        path = Path(dosya)

        if not path.exists():
            print(f"  ❌ Dosya bulunamadı: {dosya}")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                numaralar = [
                    line.strip()
                    for line in f
                    if line.strip()
                ]

        except OSError as e:
            print(f"  ❌ Dosya okunamadı: {e}")
            return

        print(f"\n{BOLD}{C}📊 TOPLU NUMARA ANALİZİ{N}")
        print("=" * 50)
        print(f"  📄 Dosya: {dosya}")
        print(f"  📞 Toplam: {len(numaralar)}")
        print("=" * 50)

        for i, num in enumerate(numaralar, 1):
            print(f"\n  [{i}/{len(numaralar)}] {num}")

            sonuc = self.tum_bilgiler(
                num,
                sessiz=True
            )

            print(f"     Ülke: {sonuc.get('ulke', '?')}")
            print(f"     Tip: {sonuc.get('tip', '?')}")
            print(f"     Operatör: {sonuc.get('operator', '?')}")
            print(f"     Geçerli: {sonuc.get('gecerli', False)}")

        print("\n" + "=" * 50)

    # --------------------------------------------------------
    # RAPOR EXPORT
    # --------------------------------------------------------

    def export_rapor(self, numara, format="json"):

        data = self.tum_bilgiler(
            numara,
            sessiz=True
        )

        timestamp = int(time.time())
        temiz = self.temizle(numara)

        if not temiz:
            temiz = "numara"

        try:

            # JSON
            if format.lower() == "json":

                path = REPORT_DIR / (
                    f"rapor_{temiz}_{timestamp}.json"
                )

                with open(
                    path,
                    "w",
                    encoding="utf-8"
                ) as f:
                    json.dump(
                        data,
                        f,
                        indent=2,
                        ensure_ascii=False
                    )

                print(f"  ✅ JSON: {path}")
                return path

            # CSV
            if format.lower() == "csv":

                path = REPORT_DIR / (
                    f"rapor_{temiz}_{timestamp}.csv"
                )

                with open(
                    path,
                    "w",
                    encoding="utf-8-sig",
                    newline=""
                ) as f:

                    writer = csv.writer(f)
                    writer.writerow([
                        "Bilgi",
                        "Değer"
                    ])

                    for key, value in data.items():

                        if isinstance(value, (dict, list)):
                            value = json.dumps(
                                value,
                                ensure_ascii=False
                            )

                        writer.writerow([
                            key,
                            value
                        ])

                print(f"  ✅ CSV: {path}")
                return path

            # PDF
            if format.lower() == "pdf":

                try:
                    from reportlab.lib.pagesizes import A4
                    from reportlab.pdfgen import canvas
                    from reportlab.pdfbase import pdfmetrics
                    from reportlab.pdfbase.ttfonts import TTFont

                except ImportError:
                    print(
                        "  ❌ reportlab yok. "
                        "pip install reportlab"
                    )
                    return None

                path = REPORT_DIR / (
                    f"rapor_{temiz}_{timestamp}.pdf"
                )

                c = canvas.Canvas(
                    str(path),
                    pagesize=A4
                )

                width, height = A4

                # Unicode font bulmaya çalış
                font_name = "Helvetica"

                possible_fonts = [
                    "/usr/share/fonts/truetype/dejavu/"
                    "DejaVuSans.ttf",
                    "/usr/share/fonts/dejavu/"
                    "DejaVuSans.ttf",
                    "/System/Library/Fonts/"
                    "Supplemental/Arial Unicode.ttf",
                ]

                for font_path in possible_fonts:
                    if os.path.exists(font_path):
                        try:
                            pdfmetrics.registerFont(
                                TTFont(
                                    "DejaVuCustom",
                                    font_path
                                )
                            )
                            font_name = "DejaVuCustom"
                            break
                        except Exception:
                            pass

                c.setFont(font_name, 16)

                c.drawString(
                    40,
                    height - 50,
                    "Numara Raporu"
                )

                c.setFont(font_name, 10)

                y = height - 80

                for key, value in data.items():

                    if isinstance(value, (dict, list)):
                        value = json.dumps(
                            value,
                            ensure_ascii=False
                        )

                    text = f"{key}: {value}"

                    # Uzun satırları kısalt
                    if len(text) > 110:
                        text = text[:107] + "..."

                    c.drawString(
                        40,
                        y,
                        text
                    )

                    y -= 18

                    if y < 50:
                        c.showPage()
                        c.setFont(font_name, 10)
                        y = height - 50

                c.save()

                print(f"  ✅ PDF: {path}")
                return path

            print("  ❌ Desteklenmeyen format.")
            return None

        except Exception as e:
            print(f"  ❌ Rapor oluşturma hatası: {e}")
            return None

    # --------------------------------------------------------
    # SOSYAL MEDYA
    # --------------------------------------------------------

    def sosyal_medya_kontrol(self, numara):

        print(
            f"\n{BOLD}{C}"
            "🌐 PLATFORM ERİŞİLEBİLİRLİĞİ"
            f"{N}"
        )

        print("=" * 50)

        print(
            "⚠️ Bu özellik telefon numarasının sosyal medya"
        )
        print(
            "   hesabını tespit etmez; sadece sitelerin"
        )
        print(
            "   erişilebilir olup olmadığını kontrol eder."
        )

        print("=" * 50)

        platformlar = {
            "Instagram": "https://www.instagram.com/",
            "Twitter/X": "https://twitter.com/",
            "Telegram": "https://t.me/",
            "Viber": "https://www.viber.com/",
            "Signal": "https://signal.org/",
            "Facebook": "https://www.facebook.com/",
        }

        for platform, url in platformlar.items():

            try:
                response = self.session.get(
                    url,
                    timeout=5,
                    allow_redirects=True
                )

                durum = (
                    "✅ Erişilebilir"
                    if response.ok
                    else f"⚠️ HTTP {response.status_code}"
                )

            except requests.RequestException:
                durum = "❌ Erişilemedi"

            print(
                f"  {platform:<12}: {durum}"
            )

        print("=" * 50)

    # --------------------------------------------------------
    # KARA LİSTE
    # --------------------------------------------------------

    def numara_engelle(self, numara):

        global KARA_LISTE

        temiz = self.temizle(numara)

        if not temiz:
            print("  ❌ Geçerli numara gir.")
            return

        if temiz not in KARA_LISTE:

            KARA_LISTE.append(temiz)

            if kara_liste_kaydet():
                print(
                    f"  ✅ {temiz} kara listeye eklendi."
                )

        else:
            print(
                "  ⚠️ Numara zaten kara listede."
            )

    # --------------------------------------------------------
    # REHBER KAYDET
    # --------------------------------------------------------

    def rehber_kaydet(self, ad, numara):

        global TELEFON_DEFTERI

        ad = ad.strip()
        numara = numara.strip()

        if not ad or not numara:
            print("  ❌ İsim ve numara gerekli.")
            return False

        TELEFON_DEFTERI.append({
            "ad": ad,
            "numara": numara,
            "tarih": datetime.now().isoformat()
        })

        if defter_kaydet():
            print(
                f"  ✅ {ad} ({numara}) kaydedildi."
            )
            return True

        return False

    # --------------------------------------------------------
    # REHBER GÖSTER
    # --------------------------------------------------------

    def rehber_goster(self):

        print(f"\n{BOLD}{C}📖 TELEFON DEFTERİ{N}")
        print("=" * 50)

        if not TELEFON_DEFTERI:
            print("  📭 Rehber boş.")
            print("=" * 50)
            return

        for i, kisi in enumerate(
            TELEFON_DEFTERI,
            1
        ):
            print(
                f"  {i}. "
                f"{kisi.get('ad', '?')} - "
                f"{kisi.get('numara', '?')}"
            )

            tarih = kisi.get("tarih", "")

            if tarih:
                print(
                    f"     📅 {tarih[:19]}"
                )

        print("=" * 50)

    # --------------------------------------------------------
    # TELEFONDA ARA
    # --------------------------------------------------------

    def telefonda_ara(self, isim):

        bulundu = False

        for kisi in TELEFON_DEFTERI:

            if isim.lower() in kisi.get(
                "ad",
                ""
            ).lower():

                bulundu = True

                print(
                    f"  📞 {kisi.get('ad')}: "
                    f"{kisi.get('numara')} "
                    f"({kisi.get('tarih', '')[:16]})"
                )

        if not bulundu:
            print("  ❌ Kayıt bulunamadı.")

    # --------------------------------------------------------
    # KARŞILAŞTIR
    # --------------------------------------------------------

    def karsilastir(self, numara1, numara2):

        print(f"\n{BOLD}{C}🔍 NUMARA KARŞILAŞTIRMA{N}")
        print("=" * 50)

        bilgi1 = self.tum_bilgiler(
            numara1,
            sessiz=True
        )

        bilgi2 = self.tum_bilgiler(
            numara2,
            sessiz=True
        )

        print(
            f"  📞 1: "
            f"{bilgi1.get('numara', numara1)}"
        )

        print(
            f"  📞 2: "
            f"{bilgi2.get('numara', numara2)}"
        )

        print("-" * 50)

        alanlar = [
            ("ulke", "📍 Ülke"),
            ("operator", "📱 Operatör"),
            ("tip", "📶 Tip"),
            ("gecerli", "✅ Geçerli"),
            ("konum", "🏙️ Konum"),
        ]

        for key, label in alanlar:

            print(
                f"  {label:<15}: "
                f"{bilgi1.get(key, '?')} "
                f"vs "
                f"{bilgi2.get(key, '?')}"
            )

        print("=" * 50)

    # --------------------------------------------------------
    # SMS BOMBER - SADECE SİMÜLASYON
    # --------------------------------------------------------

    def sms_bomber(self, numara, adet=10):

        adet = max(1, min(adet, 100))

        print(
            f"\n{BOLD}{Y}"
            "📱 SMS BOMBER - SİMÜLASYON"
            f"{N}"
        )

        print("=" * 50)
        print(f"  Hedef: {numara}")
        print(f"  Adet: {adet}")
        print()
        print(
            "  ⚠️ Gerçek SMS gönderilmez."
        )

        for i in range(adet):

            print(
                f"  📤 SMS "
                f"{i + 1}/{adet} simülasyonu..."
            )

            time.sleep(0.1)

        print("=" * 50)

    # --------------------------------------------------------
    # CALL BOMBER - SADECE SİMÜLASYON
    # --------------------------------------------------------

    def call_bomber(self, numara, adet=5):

        adet = max(1, min(adet, 100))

        print(
            f"\n{BOLD}{Y}"
            "📞 CALL BOMBER - SİMÜLASYON"
            f"{N}"
        )

        print("=" * 50)
        print(f"  Hedef: {numara}")
        print(f"  Adet: {adet}")
        print()
        print(
            "  ⚠️ Gerçek arama yapılmaz."
        )

        for i in range(adet):

            print(
                f"  📞 Arama "
                f"{i + 1}/{adet} simülasyonu..."
            )

            time.sleep(0.1)

        print("=" * 50)

    # --------------------------------------------------------
    # NUMARA TAŞINABİLİRLİĞİ
    # --------------------------------------------------------

    def numara_tasima_kontrol(self, numara):

        print(
            f"\n{BOLD}{C}"
            "🔀 NUMARA TAŞINABİLİRLİĞİ"
            f"{N}"
        )

        print("=" * 50)
        print(f"  📞 Numara: {numara}")

        operator = self.operator_bul(numara)

        print(
            f"  📱 Kaynak operatör bilgisi: "
            f"{operator}"
        )

        print()
        print(
            "  ℹ️ Gerçek numara taşınabilirliği için"
        )
        print(
            "     operatör/numara taşıma verisi gerekir."
        )
        print(
            "  ❌ Rastgele sonuç üretilmiyor."
        )

        print("=" * 50)

    # --------------------------------------------------------
    # TÜM BİLGİLER
    # --------------------------------------------------------

    def tum_bilgiler(self, numara, sessiz=False):

        formatli = self.formatla(numara)

        if not formatli:

            return {
                "numara": numara,
                "hata": "Geçersiz numara formatı."
            }

        self.sorgu_gecmisi.append({
            "numara": formatli,
            "tarih": datetime.now().isoformat()
        })

        ulke = self.ulke_bul(formatli)

        ulke_bilgi = (
            f"{ulke['adi']} (+{ulke['kod']})"
            if ulke
            else "Bilinmiyor"
        )

        operator = self.operator_bul(formatli)
        tip = self.tip_bul(formatli)
        gecerli = self.gecerli_mi(formatli)
        mumkun = self.mumkun_mu(formatli)
        konum = self.konum_bul(formatli)
        zaman_dilimleri = self.zaman_dilimi_bul(
            formatli
        )

        # WhatsApp genel lookup desteklenmediği için
        # None dönüyor.
        self.wa = self.whatsapp_kontrol(
            self.temizle(formatli)
        )

        spam = self.truecaller_spam_kontrol(
            self.temizle(formatli)
        )

        if not sessiz:

            print(
                f"\n{BOLD}{C}"
                "📊 NUMARA ANALİZİ"
                f"{N}"
            )

            print("=" * 50)

            print(
                f"  📞 Numara       : {formatli}"
            )

            print(
                f"  📍 Ülke         : {ulke_bilgi}"
            )

            print(
                f"  📱 Operatör     : {operator}"
            )

            print(
                f"  📶 Numara Tipi  : {tip}"
            )

            print(
                f"  🔎 Mümkün       : "
                f"{'✅ Evet' if mumkun else '❌ Hayır'}"
            )

            print(
                f"  ✅ Geçerlilik   : "
                f"{'✅ Geçerli' if gecerli else '❌ Geçersiz'}"
            )

            print(
                f"  🏙️ Konum        : {konum}"
            )

            print(
                f"  🕐 Zaman Dilimi : "
                f"{', '.join(zaman_dilimleri) if zaman_dilimleri else 'Bilinmiyor'}"
            )

            print(
                "  💬 WhatsApp     : "
                "⚠️ Genel kayıt kontrolü desteklenmiyor"
            )

            if spam.get("spam"):
                print(
                    f"  🛡️ Kara Liste   : "
                    f"⚠️ {spam.get('rapor', 0)} eşleşme"
                )
            else:
                print(
                    "  🛡️ Kara Liste   : ✅ Temiz"
                )

            print("=" * 50)

        return {
            "numara": formatli,
            "ulke": ulke_bilgi,
            "operator": operator,
            "tip": tip,
            "mumkun": mumkun,
            "gecerli": gecerli,
            "konum": konum,
            "zaman_dilimleri": zaman_dilimleri,
            "whatsapp": None,
            "spam": spam
        }


# ============================================================
# TWILIO
# ============================================================

class TwilioEntegrasyon:

    def __init__(self):

        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.client = None

        self.numaralar = []

        self.dosya = TWILIO_NUMARALAR_DOSYASI

        self.yukle()

        if self.account_sid and self.auth_token:
            self.baglanti_kur()

    # --------------------------------------------------------

    def yukle(self):

        data = json_yukle(
            self.dosya,
            []
        )

        self.numaralar = (
            data if isinstance(data, list)
            else []
        )

    # --------------------------------------------------------

    def kaydet(self):

        return json_kaydet(
            self.dosya,
            self.numaralar
        )

    # --------------------------------------------------------

    def baglanti_kur(self):

        try:

            from twilio.rest import Client

            self.client = Client(
                self.account_sid,
                self.auth_token
            )

            self.client.api.v2010.accounts(
                self.account_sid
            ).fetch()

            return True

        except Exception as e:

            self.client = None

            print(
                f"  ❌ Twilio bağlantı hatası: {e}"
            )

            return False

    # --------------------------------------------------------

    def manuel_giris(self):

        print(
            f"\n{BOLD}{C}"
            "🔐 MANUEL TWILIO GİRİŞİ"
            f"{N}"
        )

        print("=" * 50)

        sid = input(
            "Account SID: "
        ).strip()

        token = input(
            "Auth Token: "
        ).strip()

        if not sid or not token:

            print(
                "  ❌ SID ve Auth Token gerekli."
            )

            return False

        self.account_sid = sid
        self.auth_token = token

        return self.baglanti_kur()

    # --------------------------------------------------------

    def otomatik_giris(self, email=""):

        print(
            "\n  ℹ️ Otomatik Twilio web girişi "
            "kullanılmıyor."
        )

        return self.manuel_giris()

    # --------------------------------------------------------

    def numara_satin_al(self, ulke="US"):

        if not self.client:

            print(
                "  ❌ Önce Twilio bağlantısı kur."
            )

            return None

        ulke = ulke.upper()

        # Menüde GB seçilebilir fakat
        # gerçek uygunluk hesabı Twilio tarafında
        # ülke/numara tipine göre değişebilir.
        if ulke not in {"US", "GB"}:

            print(
                "  ❌ Bu sürümde US veya GB seç."
            )

            return None

        try:

            print(
                f"\n{BOLD}{C}"
                f"📞 NUMARA ARANIYOR ({ulke})"
                f"{N}"
            )

            available = (
                self.client
                .available_phone_numbers(ulke)
                .local
                .list(limit=1)
            )

            if not available:

                print(
                    "  ❌ Uygun numara bulunamadı."
                )

                return None

            phone_number = (
                available[0].phone_number
            )

            print(
                f"  📞 Bulunan: {phone_number}"
            )

            incoming = (
                self.client
                .incoming_phone_numbers
                .create(
                    phone_number=phone_number
                )
            )

            entry = {
                "numara": incoming.phone_number,
                "sid": incoming.sid,
                "ulke": ulke,
                "alindigi_tarih": datetime.now().isoformat(),
                "durum": "Aktif"
            }

            self.numaralar.append(entry)
            self.kaydet()

            print(
                f"  ✅ Numara alındı: "
                f"{incoming.phone_number}"
            )

            print(
                f"  🆔 SID: {incoming.sid}"
            )

            return entry

        except Exception as e:

            print(
                f"  ❌ Numara alma hatası: {e}"
            )

            return None

    # --------------------------------------------------------

    def sms_gonder(self, numara, mesaj):

        if not self.client:

            print(
                "  ❌ Twilio bağlantısı yok."
            )

            return False

        if not self.numaralar:

            print(
                "  ❌ Kayıtlı Twilio numarası yok."
            )

            return False

        if numara.startswith("whatsapp:"):

            print(
                "  ❌ WhatsApp için "
                "whatsapp_gonder() kullan."
            )

            return False

        try:

            from_number = self.numaralar[0]["numara"]

            message = self.client.messages.create(
                body=mesaj,
                from_=from_number,
                to=numara
            )

            print(
                f"  ✅ SMS gönderildi."
            )

            print(
                f"  🆔 SID: {message.sid}"
            )

            return True

        except Exception as e:

            print(
                f"  ❌ SMS hatası: {e}"
            )

            return False

    # --------------------------------------------------------

    def whatsapp_gonder(self, numara, mesaj):

        if not self.client:

            print(
                "  ❌ Twilio bağlantısı yok."
            )

            return False

        if not self.numaralar:

            print(
                "  ❌ Kayıtlı Twilio numarası yok."
            )

            return False

        try:

            to_number = (
                numara
                if numara.startswith("whatsapp:")
                else f"whatsapp:{numara}"
            )

            from_number = (
                f"whatsapp:"
                f"{self.numaralar[0]['numara']}"
            )

            message = self.client.messages.create(
                body=mesaj,
                from_=from_number,
                to=to_number
            )

            print(
                f"  ✅ WhatsApp mesajı gönderildi."
            )

            print(
                f"  🆔 SID: {message.sid}"
            )

            return True

        except Exception as e:

            print(
                f"  ❌ WhatsApp hatası: {e}"
            )

            return False

    # --------------------------------------------------------

    def mesaj_getir(self, message_sid):

        if not self.client:
            print("  ❌ Twilio bağlantısı yok.")
            return None

        if not message_sid:
            print("  ❌ Message SID gerekli.")
            return None

        try:

            message = (
                self.client
                .messages(message_sid)
                .fetch()
            )

            print(
                f"\n  📩 Mesaj: {message.body}"
            )

            print(
                f"  📞 From: {message.from_}"
            )

            print(
                f"  📞 To: {message.to}"
            )

            print(
                f"  📅 Tarih: {message.date_sent}"
            )

            print(
                f"  📊 Durum: {message.status}"
            )

            return message

        except Exception as e:

            print(
                f"  ❌ Mesaj getirme hatası: {e}"
            )

            return None

    # --------------------------------------------------------

    def mesaj_listele(self, limit=10):

        if not self.client:

            print(
                "  ❌ Twilio bağlantısı yok."
            )

            return []

        limit = max(
            1,
            min(limit, 100)
        )

        try:

            messages = (
                self.client
                .messages
                .list(limit=limit)
            )

            print(
                f"\n{BOLD}{C}"
                f"📋 SON {limit} MESAJ"
                f"{N}"
            )

            print("=" * 50)

            for msg in messages:

                body = msg.body or ""

                print(
                    f"  📩 {body[:50]}"
                )

                print(
                    f"     {msg.from_} → {msg.to}"
                )

                print(
                    f"     Durum: {msg.status}"
                )

                print(
                    "  " + "-" * 40
                )

            return messages

        except Exception as e:

            print(
                f"  ❌ Mesaj listeleme hatası: {e}"
            )

            return []

    # --------------------------------------------------------

    def numara_listele(self):

        if not self.numaralar:

            print(
                "  📭 Kayıtlı numara yok."
            )

            return

        print(
            f"\n{BOLD}{C}"
            "📋 TWILIO NUMARALARI"
            f"{N}"
        )

        print("=" * 50)

        for i, number in enumerate(
            self.numaralar,
            1
        ):

            print(
                f"  {i}. "
                f"{number.get('numara', '?')} "
                f"({number.get('ulke', '?')})"
            )

            print(
                f"     SID: "
                f"{number.get('sid', '?')}"
            )

            print(
                f"     Durum: "
                f"{number.get('durum', '?')}"
            )

        print("=" * 50)

    # --------------------------------------------------------

    def numara_iptal(self, index):

        if not self.client:

            print(
                "  ❌ Twilio bağlantısı yok."
            )

            return False

        if index < 1 or index > len(self.numaralar):

            print(
                "  ❌ Geçersiz sıra."
            )

            return False

        number = self.numaralar[index - 1]

        try:

            self.client \
                .incoming_phone_numbers(
                    number["sid"]
                ) \
                .delete()

            number["durum"] = "İptal Edildi"

            self.kaydet()

            print(
                "  ✅ Numara iptal edildi."
            )

            return True

        except Exception as e:

            print(
                f"  ❌ İptal hatası: {e}"
            )

            return False


# ============================================================
# META WHATSAPP CLOUD API
# ============================================================

class WhatsAppGraphAPI:

    def __init__(self):

        self.access_token = META_ACCESS_TOKEN
        self.phone_number_id = PHONE_NUMBER_ID
        self.waba_id = WABA_ID
        self.api_version = WHATSAPP_API_VERSION

        self.base_url = WHATSAPP_GRAPH_API

        self.session = requests.Session()

    # --------------------------------------------------------

    def _url(self, path):

        if not self.api_version:
            raise ValueError(
                "WHATSAPP_API_VERSION ayarlanmamış."
            )

        return (
            f"{self.base_url}/"
            f"{self.api_version}/"
            f"{path.lstrip('/')}"
        )

    # --------------------------------------------------------

    def _headers(self, json_content=True):

        headers = {
            "Authorization":
                f"Bearer {self.access_token}"
        }

        if json_content:
            headers["Content-Type"] = (
                "application/json"
            )

        return headers

    # --------------------------------------------------------

    def _hazir_mi(self, waba=False):

        if not self.access_token:

            print(
                "  ❌ META_ACCESS_TOKEN ayarlanmamış."
            )

            return False

        if not self.phone_number_id:

            print(
                "  ❌ PHONE_NUMBER_ID ayarlanmamış."
            )

            return False

        if not self.api_version:

            print(
                "  ❌ WHATSAPP_API_VERSION ayarlanmamış."
            )

            return False

        if waba and not self.waba_id:

            print(
                "  ❌ WABA_ID ayarlanmamış."
            )

            return False

        return True

    # --------------------------------------------------------
    # MESAJ
    # --------------------------------------------------------

    def mesaj_gonder(self, to_number, mesaj):

        if not self._hazir_mi():
            return False

        to_number = sadece_rakamlar(
            to_number
        )

        if not to_number:

            print(
                "  ❌ Hedef numara geçersiz."
            )

            return False

        if not mesaj.strip():

            print(
                "  ❌ Mesaj boş olamaz."
            )

            return False

        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": mesaj
            }
        }

        try:

            response = self.session.post(
                self._url(
                    f"{self.phone_number_id}/messages"
                ),
                headers=self._headers(),
                json=payload,
                timeout=15
            )

            if response.ok:

                data = response.json()

                messages = data.get(
                    "messages",
                    []
                )

                message_id = (
                    messages[0].get("id")
                    if messages
                    else "?"
                )

                print(
                    f"  ✅ WhatsApp mesajı gönderildi."
                )

                print(
                    f"  🆔 ID: {message_id}"
                )

                return True

            print(
                f"  ❌ Meta HTTP "
                f"{response.status_code}"
            )

            print(
                f"  📄 {response.text[:1000]}"
            )

            return False

        except requests.RequestException as e:

            print(
                f"  ❌ Bağlantı hatası: {e}"
            )

            return False

    # --------------------------------------------------------
    # TELEFON NUMARALARI
    # --------------------------------------------------------

    def telefon_numaralari(self):

        if not self._hazir_mi(waba=True):
            return []

        try:

            response = self.session.get(
                self._url(
                    f"{self.waba_id}/phone_numbers"
                ),
                headers=self._headers(
                    json_content=False
                ),
                timeout=15
            )

            if not response.ok:

                print(
                    f"  ❌ HTTP "
                    f"{response.status_code}"
                )

                print(
                    response.text[:1000]
                )

                return []

            data = response.json()

            numbers = data.get(
                "data",
                []
            )

            print(
                f"\n  📞 {len(numbers)} "
                "telefon numarası bulundu."
            )

            for number in numbers:

                print(
                    f"     📱 "
                    f"{number.get('display_phone_number', '?')}"
                )

                print(
                    f"        ID: "
                    f"{number.get('id', '?')}"
                )

            return numbers

        except requests.RequestException as e:

            print(
                f"  ❌ API hatası: {e}"
            )

            return []

    # --------------------------------------------------------
    # WABA BİLGİLERİ
    # --------------------------------------------------------

    def waba_bilgileri(self):

        if not self._hazir_mi(waba=True):
            return None

        try:

            response = self.session.get(
                self._url(
                    self.waba_id
                ),
                headers=self._headers(
                    json_content=False
                ),
                timeout=15
            )

            if not response.ok:

                print(
                    f"  ❌ HTTP "
                    f"{response.status_code}"
                )

                print(
                    response.text[:1000]
                )

                return None

            data = response.json()

            print(
                f"\n{BOLD}{C}"
                "📊 WABA BİLGİLERİ"
                f"{N}"
            )

            print("=" * 50)

            for key, value in data.items():

                print(
                    f"  {key}: {value}"
                )

            print("=" * 50)

            return data

        except requests.RequestException as e:

            print(
                f"  ❌ WABA hatası: {e}"
            )

            return None

    # --------------------------------------------------------
    # MEDYA YÜKLE
    # --------------------------------------------------------

    def media_yukle(self, dosya_yolu):

        if not self._hazir_mi():
            return None

        path = Path(dosya_yolu)

        if not path.exists():

            print(
                "  ❌ Dosya bulunamadı."
            )

            return None

        if not path.is_file():

            print(
                "  ❌ Bu bir dosya değil."
            )

            return None

        try:

            url = self._url(
                f"{self.phone_number_id}/media"
            )

            headers = self._headers(
                json_content=False
            )

            with open(
                path,
                "rb"
            ) as file:

                files = {
                    "file": (
                        path.name,
                        file,
                        "application/octet-stream"
                    )
                }

                data = {
                    "messaging_product":
                        "whatsapp"
                }

                response = self.session.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=60
                )

            if response.ok:

                result = response.json()

                media_id = result.get("id")

                print(
                    f"  ✅ Medya yüklendi."
                )

                print(
                    f"  🆔 ID: {media_id}"
                )

                return media_id

            print(
                f"  ❌ HTTP "
                f"{response.status_code}"
            )

            print(
                response.text[:1000]
            )

            return None

        except requests.RequestException as e:

            print(
                f"  ❌ Medya yükleme hatası: {e}"
            )

            return None

        except OSError as e:

            print(
                f"  ❌ Dosya hatası: {e}"
            )

            return None

    # --------------------------------------------------------
    # MEDYA BİLGİSİ
    # --------------------------------------------------------

    def media_bilgisi(self, media_id):

        if not self._hazir_mi():
            return None

        media_id = str(media_id).strip()

        if not media_id:
            print("  ❌ Media ID gerekli.")
            return None

        try:

            response = self.session.get(
                self._url(media_id),
                headers=self._headers(
                    json_content=False
                ),
                timeout=15
            )

            if response.ok:

                data = response.json()

                print(
                    f"\n{BOLD}{C}"
                    "📎 MEDYA BİLGİSİ"
                    f"{N}"
                )

                print("=" * 50)

                for key, value in data.items():

                    print(
                        f"  {key}: {value}"
                    )

                print("=" * 50)

                return data

            print(
                f"  ❌ HTTP "
                f"{response.status_code}"
            )

            print(
                response.text[:1000]
            )

            return None

        except requests.RequestException as e:

            print(
                f"  ❌ Medya hatası: {e}"
            )

            return None

    # --------------------------------------------------------
    # MEDYA SİL
    # --------------------------------------------------------

    def media_sil(self, media_id):

        if not self._hazir_mi():
            return False

        media_id = str(media_id).strip()

        if not media_id:
            print("  ❌ Media ID gerekli.")
            return False

        try:

            response = self.session.delete(
                self._url(media_id),
                headers=self._headers(
                    json_content=False
                ),
                timeout=15
            )

            if response.ok:

                print(
                    f"  ✅ Medya silindi: "
                    f"{media_id}"
                )

                return True

            print(
                f"  ❌ HTTP "
                f"{response.status_code}"
            )

            print(
                response.text[:1000]
            )

            return False

        except requests.RequestException as e:

            print(
                f"  ❌ Medya silme hatası: {e}"
            )

            return False


# ============================================================
# FLASK WEB PANEL
# ============================================================

class WebPanel:

    @staticmethod
    def start():

        print(
            f"\n{BOLD}{C}"
            "🌐 WEB PANEL"
            f"{N}"
        )

        print("=" * 50)
        print(
            "  http://127.0.0.1:5000"
        )
        print("=" * 50)

        try:

            from flask import (
                Flask,
                jsonify,
                request
            )

        except ImportError:

            print(
                "  ❌ Flask yüklü değil."
            )

            print(
                "  pip install flask"
            )

            return

        app = Flask(__name__)

        app.secret_key = FLASK_SECRET_KEY

        sorgu = NumaraSorgula()

        @app.route("/", methods=["GET"])
        def index():

            return """
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>Numara Çözüm</title>
<style>
body {
    font-family: Arial, sans-serif;
    max-width: 700px;
    margin: 40px auto;
    padding: 20px;
}
input {
    width: 70%;
    padding: 10px;
}
button {
    padding: 10px 20px;
}
pre {
    background: #f4f4f4;
    padding: 15px;
    white-space: pre-wrap;
}
</style>
</head>
<body>
<h1>📱 Numara Çözüm Tool'u</h1>

<form method="POST" action="/sorgu">
    <input
        type="text"
        name="numara"
        placeholder="+905xxxxxxxxx"
        required
    >
    <button type="submit">
        Sorgula
    </button>
</form>

</body>
</html>
"""

        @app.route(
            "/sorgu",
            methods=["POST"]
        )
        def sorgu_route():

            numara = (
                request.form.get(
                    "numara",
                    ""
                ).strip()
            )

            if not numara:

                return jsonify({
                    "hata": "Numara gerekli."
                }), 400

            sonuc = sorgu.tum_bilgiler(
                numara,
                sessiz=True
            )

            return jsonify(sonuc)

        try:

            app.run(
                host="127.0.0.1",
                port=5000,
                debug=False
            )

        except Exception as e:

            print(
                f"  ❌ Flask hatası: {e}"
            )


# ============================================================
# MENÜ
# ============================================================

def menu():

    version_text = (
        WHATSAPP_API_VERSION
        if WHATSAPP_API_VERSION
        else "ayarlanmadı"
    )

    print(
        f"""
╔═══════════════════════════════════════════════════════════╗
║  {C}📱 {APP_NAME} v{APP_VERSION}{N}                         ║
║  {Y}Meta Graph API: {version_text:<35}{N}║
╚═══════════════════════════════════════════════════════════╝

{B}1.{N} 🔍 Numara Sorgula
{B}2.{N} 💬 Twilio İşlemleri
{B}3.{N} 💬 WhatsApp Meta Cloud API
{B}4.{N} 🎲 Numara Üretici / Tahmin
{B}5.{N} 📊 Toplu Numara Analizi
{B}6.{N} 🔍 Numara Karşılaştırma
{B}7.{N} 🌐 Platform Erişilebilirlik Kontrolü
{B}8.{N} 📤 Rapor Dışa Aktar
{B}9.{N} 📞 SMS/Call Simülasyonu
{B}10.{N} 🛡️ Kara Liste
{B}11.{N} 📖 Telefon Defteri
{B}12.{N} 🌐 Web Panel
{B}13.{N} 🤖 Telegram
{B}14.{N} 🔀 Numara Taşınabilirliği
{B}0.{N} ❌ Çıkış
"""
    )


# ============================================================
# TWILIO MENÜ
# ============================================================

def menu_twilio():

    twilio = TwilioEntegrasyon()

    while True:

        temizle()

        print(
            f"""
╔═══════════════════════════════════════════════════════════╗
║  {C}💬 TWILIO İŞLEMLERİ{N}                                  ║
╚═══════════════════════════════════════════════════════════╝

{B}1.{N} 🔐 Manuel Giriş
{B}2.{N} 📞 Numara Al
{B}3.{N} 📋 Numaraları Listele
{B}4.{N} 📤 SMS Gönder
{B}5.{N} 💬 WhatsApp Mesajı
{B}6.{N} 📩 Mesaj Getir
{B}7.{N} 📋 Mesajları Listele
{B}8.{N} 🗑️ Numara İptal Et
{B}0.{N} Ana Menü
"""
        )

        secim = input(
            "Seçim: "
        ).strip()

        if secim == "0":
            break

        elif secim == "1":

            twilio.manuel_giris()
            bekle()

        elif secim == "2":

            if not twilio.client:

                print(
                    "  ❌ Önce giriş yap."
                )

            else:

                ulke = (
                    input(
                        "Ülke (US/GB): "
                    )
                    .strip()
                    .upper()
                    or "US"
                )

                twilio.numara_satin_al(
                    ulke
                )

            bekle()

        elif secim == "3":

            twilio.numara_listele()
            bekle()

        elif secim == "4":

            if not twilio.client:

                print(
                    "  ❌ Önce giriş yap."
                )

            elif not twilio.numaralar:

                print(
                    "  ❌ Önce Twilio numarası al."
                )

            else:

                numara = input(
                    "📞 Hedef: "
                ).strip()

                mesaj = input(
                    "💬 Mesaj: "
                ).strip()

                if numara and mesaj:
                    twilio.sms_gonder(
                        numara,
                        mesaj
                    )

            bekle()

        elif secim == "5":

            if not twilio.client:

                print(
                    "  ❌ Önce giriş yap."
                )

            elif not twilio.numaralar:

                print(
                    "  ❌ Önce Twilio numarası al."
                )

            else:

                numara = input(
                    "📞 WhatsApp hedefi: "
                ).strip()

                mesaj = input(
                    "💬 Mesaj: "
                ).strip()

                if numara and mesaj:
                    twilio.whatsapp_gonder(
                        numara,
                        mesaj
                    )

            bekle()

        elif secim == "6":

            sid = input(
                "Message SID: "
            ).strip()

            twilio.mesaj_getir(sid)

            bekle()

        elif secim == "7":

            limit = safe_int_input(
                "Kaç mesaj? (10): ",
                10,
                minimum=1,
                maximum=100
            )

            twilio.mesaj_listele(
                limit
            )

            bekle()

        elif secim == "8":

            twilio.numara_listele()

            index = safe_int_input(
                "İptal sıra numarası: ",
                0,
                minimum=1
            )

            if index:
                twilio.numara_iptal(
                    index
                )

            bekle()

        else:

            print(
                "  ❌ Geçersiz seçim."
            )

            time.sleep(1)


# ============================================================
# META WHATSAPP MENÜ
# ============================================================

def menu_whatsapp_meta():

    whatsapp = WhatsAppGraphAPI()

    while True:

        temizle()

        version = (
            WHATSAPP_API_VERSION
            or "ayarlanmadı"
        )

        print(
            f"""
╔═══════════════════════════════════════════════════════════╗
║  {C}💬 META WHATSAPP CLOUD API{N}                           ║
║  {Y}Graph API: {version:<40}{N}║
╚═══════════════════════════════════════════════════════════╝

{B}1.{N} 📤 Mesaj Gönder
{B}2.{N} 📞 Telefon Numaralarını Getir
{B}3.{N} 📊 WABA Bilgilerini Getir
{B}4.{N} 📎 Medya Yükle
{B}5.{N} 📄 Medya Bilgisi
{B}6.{N} 🗑️ Medya Sil
{B}0.{N} Ana Menü
"""
        )

        secim = input(
            "Seçim: "
        ).strip()

        if secim == "0":
            break

        elif secim == "1":

            numara = input(
                "📞 Hedef numara: "
            ).strip()

            mesaj = input(
                "💬 Mesaj: "
            ).strip()

            if numara and mesaj:

                whatsapp.mesaj_gonder(
                    numara,
                    mesaj
                )

            bekle()

        elif secim == "2":

            whatsapp.telefon_numaralari()
            bekle()

        elif secim == "3":

            whatsapp.waba_bilgileri()
            bekle()

        elif secim == "4":

            dosya = input(
                "📁 Dosya yolu: "
            ).strip()

            if dosya:
                whatsapp.media_yukle(
                    dosya
                )

            bekle()

        elif secim == "5":

            media_id = input(
                "🆔 Media ID: "
            ).strip()

            whatsapp.media_bilgisi(
                media_id
            )

            bekle()

        elif secim == "6":

            media_id = input(
                "🆔 Media ID: "
            ).strip()

            whatsapp.media_sil(
                media_id
            )

            bekle()

        else:

            print(
                "  ❌ Geçersiz seçim."
            )

            time.sleep(1)


# ============================================================
# NUMARA SORGU MENÜSÜ
# ============================================================

def menu_numara_sorgula():

    sorgu = NumaraSorgula()

    while True:

        temizle()

        print(
            f"""
╔═══════════════════════════════════════════════════════════╗
║  {C}🔍 NUMARA SORGULA{N}                                    ║
╚═══════════════════════════════════════════════════════════╝

{B}1.1{N} Numara Sorgula
{B}1.2{N} WhatsApp Durumu
{B}1.3{N} Kara Liste Kontrolü
{B}1.4{N} Numara Doğrula
{B}1.5{N} Telefon Defteri
{B}1.6{N} Numara Geçmişi
{B}1.7{N} Numverify
{B}1.8{N} Prefix Tahmini
{B}1.9{N} IP Kontrolü
{B}1.10{N} Taşınabilirlik
{B}0.{N} Ana Menü
"""
        )

        secim = input(
            "Seçim: "
        ).strip()

        if secim == "0":
            break

        elif secim == "1.1":

            numara = input(
                "Numara: "
            ).strip()

            if numara:
                sorgu.tum_bilgiler(
                    numara
                )

            bekle()

        elif secim == "1.2":

            numara = input(
                "Numara: "
            ).strip()

            if numara:

                sonuc = sorgu.whatsapp_kontrol(
                    sorgu.temizle(numara)
                )

                if sonuc is None:

                    print(
                        "\n  ⚠️ Meta Cloud API genel"
                    )

                    print(
                        "     WhatsApp kayıt kontrolü "
                        "sağlamaz."
                    )

            bekle()

        elif secim == "1.3":

            numara = input(
                "Numara: "
            ).strip()

            if numara:

                result = (
                    sorgu.truecaller_spam_kontrol(
                        sorgu.temizle(numara)
                    )
                )

                if result["spam"]:

                    print(
                        f"\n  ⚠️ Kara listede."
                    )

                    print(
                        f"  📊 Eşleşme: "
                        f"{result['rapor']}"
                    )

                else:

                    print(
                        "\n  ✅ Yerel kara listede yok."
                    )

            bekle()

        elif secim == "1.4":

            numara = input(
                "Numara: "
            ).strip()

            if numara:

                parsed = sorgu.parse(
                    numara
                )

                formatli = sorgu.formatla(
                    numara
                )

                if parsed and formatli:

                    ulke = sorgu.ulke_bul(
                        numara
                    )

                    print(
                        "\n  ✅ Numara geçerli."
                    )

                    print(
                        f"  📍 Ülke: "
                        f"{ulke['adi'] if ulke else '?'}"
                    )

                    print(
                        f"  📱 Format: {formatli}"
                    )

                else:

                    print(
                        "\n  ❌ Geçersiz numara."
                    )

            bekle()

        elif secim == "1.5":

            sorgu.rehber_goster()
            bekle()

        elif secim == "1.6":

            print(
                f"\n{BOLD}{C}"
                "📋 NUMARA GEÇMİŞİ"
                f"{N}"
            )

            print("=" * 50)

            if not sorgu.sorgu_gecmisi:

                print(
                    "  📭 Bu oturumda sorgu yok."
                )

            else:

                for item in (
                    sorgu.sorgu_gecmisi[-20:]
                ):

                    print(
                        f"  📞 {item['numara']}"
                    )

                    print(
                        f"     "
                        f"{item['tarih'][:19]}"
                    )

            print("=" * 50)

            bekle()

        elif secim == "1.7":

            numara = input(
                "Numara: "
            ).strip()

            if numara:

                result = (
                    sorgu.numverify_dogrula(
                        numara
                    )
                )

                print(
                    f"\n{BOLD}{C}"
                    "📊 NUMVERIFY"
                    f"{N}"
                )

                print("=" * 50)

                for key, value in result.items():

                    print(
                        f"  {key}: {value}"
                    )

                print("=" * 50)

            bekle()

        elif secim == "1.8":

            prefix = input(
                "Prefix: "
            ).strip()

            if prefix:

                adet = safe_int_input(
                    "Adet (10): ",
                    10,
                    minimum=1,
                    maximum=100
                )

                sorgu.numara_tahmin(
                    prefix,
                    adet
                )

            bekle()

        elif secim == "1.9":

            numara = input(
                "Numara: "
            ).strip()

            if numara:
                sorgu.ip_bul(
                    numara
                )

            bekle()

        elif secim == "1.10":

            numara = input(
                "Numara: "
            ).strip()

            if numara:

                sorgu.numara_tasima_kontrol(
                    numara
                )

            bekle()

        else:

            print(
                "  ❌ Geçersiz seçim."
            )

            time.sleep(1)


# ============================================================
# MAIN
# ============================================================

def main():

    while True:

        temizle()
        menu()

        secim = input(
            "Seçim: "
        ).strip()

        # ----------------------------------------------------
        # ÇIKIŞ
        # ----------------------------------------------------

        if secim == "0":

            print(
                "\n👋 Çıkış yapılıyor..."
            )

            break

        # ----------------------------------------------------
        # NUMARA SORGULA
        # ----------------------------------------------------

        elif secim == "1":

            menu_numara_sorgula()

        # ----------------------------------------------------
        # TWILIO
        # ----------------------------------------------------

        elif secim == "2":

            menu_twilio()

        # ----------------------------------------------------
        # META WHATSAPP
        # ----------------------------------------------------

        elif secim == "3":

            menu_whatsapp_meta()

        # ----------------------------------------------------
        # NUMARA ÜRETİCİ
        # ----------------------------------------------------

        elif secim == "4":

            sorgu = NumaraSorgula()

            temizle()

            print(
                f"\n{BOLD}{C}"
                "🎲 NUMARA ÜRETİCİ"
                f"{N}"
            )

            print("=" * 50)

            print(
                "  1. Rastgele üret"
            )

            print(
                "  2. Prefix tahmini"
            )

            alt = input(
                "Seçim: "
            ).strip()

            if alt == "1":

                adet = safe_int_input(
                    "Adet (5): ",
                    5,
                    minimum=1,
                    maximum=100
                )

                for i in range(adet):

                    print(
                        f"  {i + 1}. "
                        f"{sorgu.numara_uret('TR')}"
                    )

            elif alt == "2":

                prefix = input(
                    "Prefix: "
                ).strip()

                if prefix:

                    adet = safe_int_input(
                        "Adet (10): ",
                        10,
                        minimum=1,
                        maximum=100
                    )

                    sorgu.numara_tahmin(
                        prefix,
                        adet
                    )

            bekle()

        # ----------------------------------------------------
        # TOPLU
        # ----------------------------------------------------

        elif secim == "5":

            sorgu = NumaraSorgula()

            dosya = input(
                "📄 Numara listesi dosyası: "
            ).strip()

            if dosya:

                sorgu.toplu_analiz(
                    dosya
                )

            bekle()

        # ----------------------------------------------------
        # KARŞILAŞTIR
        # ----------------------------------------------------

        elif secim == "6":

            sorgu = NumaraSorgula()

            n1 = input(
                "📞 1. Numara: "
            ).strip()

            n2 = input(
                "📞 2. Numara: "
            ).strip()

            if n1 and n2:

                sorgu.karsilastir(
                    n1,
                    n2
                )

            bekle()

        # ----------------------------------------------------
        # SOSYAL
        # ----------------------------------------------------

        elif secim == "7":

            sorgu = NumaraSorgula()

            numara = input(
                "📞 Numara: "
            ).strip()

            if numara:

                sorgu.sosyal_medya_kontrol(
                    numara
                )

            bekle()

        # ----------------------------------------------------
        # RAPOR
        # ----------------------------------------------------

        elif secim == "8":

            sorgu = NumaraSorgula()

            numara = input(
                "📞 Numara: "
            ).strip()

            if numara:

                print(
                    "\n  1. JSON"
                )

                print(
                    "  2. CSV"
                )

                print(
                    "  3. PDF"
                )

                fmt = input(
                    "Seçim: "
                ).strip()

                formats = {
                    "1": "json",
                    "2": "csv",
                    "3": "pdf"
                }

                sorgu.export_rapor(
                    numara,
                    formats.get(
                        fmt,
                        "json"
                    )
                )

            bekle()

        # ----------------------------------------------------
        # SİMÜLASYONLAR
        # ----------------------------------------------------

        elif secim == "9":

            sorgu = NumaraSorgula()

            numara = input(
                "📞 Hedef numara: "
            ).strip()

            if numara:

                print(
                    "\n  1. SMS Simülasyonu"
                )

                print(
                    "  2. Arama Simülasyonu"
                )

                alt = input(
                    "Seçim: "
                ).strip()

                if alt == "1":

                    adet = safe_int_input(
                        "Adet (10): ",
                        10,
                        minimum=1,
                        maximum=100
                    )

                    sorgu.sms_bomber(
                        numara,
                        adet
                    )

                elif alt == "2":

                    adet = safe_int_input(
                        "Adet (5): ",
                        5,
                        minimum=1,
                        maximum=100
                    )

                    sorgu.call_bomber(
                        numara,
                        adet
                    )

            bekle()

        # ----------------------------------------------------
        # KARA LİSTE
        # ----------------------------------------------------

        elif secim == "10":

            sorgu = NumaraSorgula()

            numara = input(
                "📞 Kara listeye eklenecek numara: "
            ).strip()

            if numara:

                sorgu.numara_engelle(
                    numara
                )

            bekle()

        # ----------------------------------------------------
        # REHBER
        # ----------------------------------------------------

        elif secim == "11":

            sorgu = NumaraSorgula()

            temizle()

            print(
                f"""
{BOLD}{C}📖 TELEFON DEFTERİ{N}

1. Kaydet
2. Ara
3. Listele
0. Geri
"""
            )

            alt = input(
                "Seçim: "
            ).strip()

            if alt == "1":

                ad = input(
                    "👤 İsim: "
                ).strip()

                numara = input(
                    "📞 Numara: "
                ).strip()

                if ad and numara:

                    sorgu.rehber_kaydet(
                        ad,
                        numara
                    )

            elif alt == "2":

                isim = input(
                    "🔍 İsim: "
                ).strip()

                if isim:
                    sorgu.telefonda_ara(
                        isim
                    )

            elif alt == "3":

                sorgu.rehber_goster()

            bekle()

        # ----------------------------------------------------
        # WEB
        # ----------------------------------------------------

        elif secim == "12":

            WebPanel.start()

        # ----------------------------------------------------
        # TELEGRAM
        # ----------------------------------------------------

        elif secim == "13":

            sorgu = NumaraSorgula()

            numara = input(
                "📞 Numara: "
            ).strip()

            if numara:

                result = (
                    sorgu.telegram_bot_sorgu(
                        numara
                    )
                )

                print(
                    f"\n  🤖 Sonuç: {result}"
                )

            bekle()

        # ----------------------------------------------------
        # TAŞINABİLİRLİK
        # ----------------------------------------------------

        elif secim == "14":

            sorgu = NumaraSorgula()

            numara = input(
                "📞 Numara: "
            ).strip()

            if numara:

                sorgu.numara_tasima_kontrol(
                    numara
                )

            bekle()

        else:

            print(
                "  ❌ Geçersiz seçim."
            )

            time.sleep(1)


# ============================================================
# PROGRAM BAŞLANGICI
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\n\n👋 Çıkış yapılıyor..."
        )

    except Exception as e:

        print(
            f"\n{R}"
            f"❌ Beklenmeyen hata: {e}"
            f"{N}"
        )

        sys.exit(1)
