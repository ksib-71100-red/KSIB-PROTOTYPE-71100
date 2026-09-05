#!/usr/bin/env python3
# KSIB ULTRA MEGA SCANNER FINAL - 47 HATA GİDERİLDİ
# pip install requests beautifulsoup4 (dnspython opsiyonel)

import socket
import ssl
import requests
import json
import sys
import os
import time
import re
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin

import urllib3
urllib3.disable_warnings()

# ============================================================
# RENKLER (TEK MERKEZ)
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
# ULTRA MEGA SCANNER
# ============================================================
class UltraMegaScanner:
    def __init__(self, target):
        self.target = target
        self.start_time = time.time()
        self.lock = threading.Lock()

        # Sonuçlar (tüm alanlar doldurulacak)
        self.results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "status": "Başlatıldı",
            "dns": {},
            "ports": [],
            "services": [],
            "os": {},
            "ssl": {},
            "headers": {},
            "cookies": [],
            "technologies": [],
            "directories": [],
            "files": [],
            "subdomains": [],
            "vulnerabilities": [],
            "emails": [],
            "links": [],
            "forms": [],
            "parameters": [],
            "javascript": [],
            "comments": [],
            "waf": None,
            "cloud": None,
            "cdn": None
        }

        # Session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        })
        self.session.timeout = 5  # 16. hata: timeout 5 sn

        # Wordlist'ler
        self.dirs = self._load_dirs()
        self.subdomains = self._load_subdomains()
        self.vuln_patterns = self._load_vuln_patterns()
        self.tech_patterns = self._load_tech_patterns()
        self.waf_signatures = self._load_waf_signatures()
        self.cloud_signatures = self._load_cloud_signatures()

        # İlerleme
        self.total_tasks = len(self.dirs) + len(self.subdomains) + 30  # 11. hata düzeltildi
        self.completed_tasks = 0
        self.found_items = 0

        # Derlenmiş regex'ler (performans)
        self._compile_regexes()

    # ======================== WORDLIST'LER ========================
    def _load_dirs(self):
        return [
            "/admin", "/admin/login", "/admin.php", "/panel", "/login", "/wp-admin",
            "/wp-login.php", "/administrator", "/cpanel", "/plesk", "/webmail",
            "/phpmyadmin", "/pma", "/myadmin", "/mysql", "/db", "/database",
            "/backup", "/backups", "/dump", "/.git", "/.env", "/.aws", "/.ssh",
            "/composer.json", "/package.json", "/requirements.txt", "/Dockerfile",
            "/.htaccess", "/web.config", "/.git/config", "/.git/HEAD",
            "/api", "/api/v1", "/graphql", "/swagger", "/docs", "/redoc",
            "/.well-known", "/.well-known/security.txt",
            "/test", "/debug", "/dev", "/sandbox", "/stage", "/staging",
            "/tmp", "/logs", "/error", "/status",
            "/backup-old", "/archive", "/data", "/download", "/uploads",
            "/wp-content", "/wp-includes", "/wp-json", "/wp-cron.php",
            "/modules", "/themes", "/plugins", "/vendor", "/node_modules",
            "/server-status", "/cgi-bin", "/favicon.ico",
            "/robots.txt", "/sitemap.xml", "/crossdomain.xml",
            "/user", "/profile", "/account", "/dashboard", "/home",
            "/shop", "/cart", "/checkout", "/product", "/products",
            "/storage", "/cdn", "/static", "/assets", "/media", "/images",
            "/phpinfo.php", "/info.php", "/test.php", "/config.php",
            "/index.php", "/index.html", "/default.php", "/default.html"
        ]

    def _load_subdomains(self):
        return [
            "www", "mail", "ftp", "dev", "test", "stage", "api", "admin", "cdn",
            "static", "blog", "shop", "docs", "support", "demo", "backup",
            "beta", "alpha", "preprod", "prod", "uat", "qa",
            "vpn", "secure", "portal", "gateway", "edge", "internal",
            "db", "mysql", "postgres", "mongodb", "redis", "elastic",
            "monitor", "grafana", "kibana", "jenkins",
            "git", "svn", "ci", "cd", "deploy", "build",
            "auth", "oauth", "sso", "login", "signin",
            "web", "app", "mobile", "m", "wap",
            "partner", "affiliate", "vendor", "customer",
            "ecommerce", "shop", "store", "cart", "payment",
            "news", "media", "video", "audio", "files"
        ]

    def _load_vuln_patterns(self):
        return {
            "SQL Injection": {
                "patterns": [
                    r"(sql|mysql|postgresql|oracle|mssql|database error|syntax error)",
                    r"(unclosed quotation|ODBC|SQLSTATE)",
                    r"(you have an error in your sql|warning.*mysql)",
                    r"(ORA-[0-9]{5}|PostgreSQL.*ERROR)"
                ],
                "severity": "Critical"
            },
            "XSS": {
                "patterns": [
                    r"(<script|alert\(|prompt\(|confirm\()",
                    r"(onerror=|onload=|onclick=|onmouseover=)",
                    r"(javascript:|data:text/html)"
                ],
                "severity": "High"
            },
            "LFI/RFI": {
                "patterns": [
                    r"(etc/passwd|windows/win.ini|boot.ini)",
                    r"(\.\./|\.\.\\|include\(|require\()"
                ],
                "severity": "Critical"
            },
            "RCE": {
                "patterns": [
                    r"(system\(|exec\(|shell_exec\(|passthru\(|eval\()",
                    r"(assert\(|preg_replace.*/e|create_function\()",
                    r"(cmd=|command=|exec=|ping=|wget=)"
                ],
                "severity": "Critical"
            },
            "PHPInfo": {
                "patterns": [
                    r"(phpinfo\(|PHP Version|Zend Engine)",
                    r"(configure command|extension_dir)"
                ],
                "severity": "High"
            },
            ".git Exposed": {
                "patterns": [
                    r"(git/HEAD|refs/heads/master|index:.*\.git)",
                    r"(/objects/|/refs/|/logs/)"
                ],
                "severity": "High"
            },
            ".env Exposed": {
                "patterns": [
                    r"(DB_HOST|DB_NAME|DB_USER|DB_PASS|DB_PASSWORD)",
                    r"(APP_KEY|APP_ENV|APP_DEBUG|APP_URL)",
                    r"(SECRET|SECRET_KEY|API_KEY)"
                ],
                "severity": "Critical"
            },
            "Directory Listing": {
                "patterns": [
                    r"(index of /|parent directory|directory listing)",
                    r"(<pre>.*<a href=|apache.*port 80)"
                ],
                "severity": "Medium"
            },
            "XXE": {
                "patterns": [
                    r"(<!DOCTYPE|<!ENTITY|SYSTEM|PUBLIC)",
                    r"(xml:.*external|xml.*entity)"
                ],
                "severity": "High"
            },
            "SSRF": {
                "patterns": [
                    r"(url=|path=|dest=|redirect=|return=|next=)",
                    r"(http://|https://|file://|gopher://)"
                ],
                "severity": "High"
            },
            "Open Redirect": {
                "patterns": [
                    r"(redirect=|return=|next=|dest=|url=|to=)",
                    r"(http://|https://|//)"
                ],
                "severity": "Medium"
            },
            "Sensitive Data": {
                "patterns": [
                    r"(\b[0-9]{16}\b|\b[0-9]{15,16}\b)",
                    r"(\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b)",
                    r"(password|parola|şifre|hesap|kart|iban)"
                ],
                "severity": "Medium"
            }
        }

    def _load_tech_patterns(self):
        return {
            "WordPress": r"(wp-content|wp-includes|wp-json|/wp-)",
            "Joomla": r"(joomla|com_content|com_users|components/com_)",
            "Drupal": r"(drupal|sites/all|modules/contrib|core/misc)",
            "Magento": r"(magento|skin/frontend|Mage::|/app/code/)",
            "Shopify": r"(shopify|myshopify.com|cdn.shopify)",
            "Laravel": r"(laravel|csrf-token|_token|/vendor/laravel)",
            "Django": r"(csrfmiddlewaretoken|django|/static/admin)",
            "React": r"(react|_reactRootContainer|ReactDOM)",
            "Angular": r"(angular|ng-app|ng-controller|ng-repeat)",
            "Vue.js": r"(vue|v-bind|v-for|v-if|v-model)",
            "Next.js": r"(next|_next/static|__NEXT_DATA__)",
            "Bootstrap": r"(bootstrap|data-bs-|col-md-|col-lg-)",
            "jQuery": r"(jquery|\$\(document\)\.ready|jQuery\()",
            "Tailwind": r"(tailwind|tw-|bg-gray-|text-)",
            "Font Awesome": r"(fa-|font-awesome|fa-solid|fa-regular)",
            "Google Analytics": r"(gtag|ga-|google-analytics|UA-\d{4,10})",
            "Cloudflare": r"(cloudflare|cf-ray|__cfduid)",
            "AWS": r"(aws|amazonaws|s3.amazonaws|cloudfront)",
            "Nginx": r"(nginx|server: nginx)",
            "Apache": r"(apache|server: apache)",
            "IIS": r"(iis|server: microsoft-iis)",
            "Node.js": r"(node|express|server: nodejs)"
        }

    def _load_waf_signatures(self):
        return {
            "Cloudflare": ["cf-ray", "__cfduid", "Cloudflare"],
            "AWS WAF": ["x-amzn-RequestId", "AWSWAF"],
            "Sucuri": ["sucuri", "x-sucuri-id"],
            "ModSecurity": ["ModSecurity", "OWASP"],
            "Wordfence": ["wordfence", "wfvt_"],
            "Akamai": ["akamai", "X-Akamai-Transformed"],
            "Imperva": ["incap_ses", "visid_incap"],
            "F5 BIG-IP": ["BigIP", "TS016b47"],
            "Barracuda": ["barracuda", "BNI__BARRACUDA"],
            "Fortinet": ["Fortinet", "FortiGate"],
            "Incapsula": ["X-CDN", "Incapsula"]
        }

    def _load_cloud_signatures(self):
        return {
            "AWS": ["x-amz", "aws", "cloudfront", "s3.amazonaws"],
            "Google Cloud": ["x-gcs", "google-cloud", "gcp"],
            "Azure": ["x-ms", "azure", "windows-azure"],
            "Cloudflare": ["cf-", "cloudflare"],
            "Akamai": ["akamai", "x-ak"],
            "Fastly": ["x-fastly", "fastly"]
        }

    def _compile_regexes(self):
        """Tüm regex'leri derle (performans)"""
        # Vuln
        for vuln_name, vuln_data in self.vuln_patterns.items():
            vuln_data["compiled"] = [re.compile(p, re.IGNORECASE) for p in vuln_data["patterns"]]

        # Tech
        self.compiled_tech = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in self.tech_patterns.items()}

        # Email, link, comment
        self.email_re = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.link_re = re.compile(r'href=[\'"]?([^\'" >]+)')
        self.comment_re = re.compile(r'<!--(.*?)-->', re.DOTALL)
        self.js_re = re.compile(r'<script[^>]*src=[\'"]?([^\'" >]+)')
        self.form_re = re.compile(r'<form', re.IGNORECASE)
        self.param_re = re.compile(r'name=[\'"]?([^\'" >]+)')

    # ======================== PRINT / PROGRESS ========================
    def safe_print(self, msg, status="info"):
        """Thread-safe print (emoji yok)"""
        icons = {
            "info": "[i]",
            "success": "[+]",
            "error": "[-]",
            "warning": "[!]",
            "scan": "[*]",
            "found": "[>]",
            "critical": "[!]"
        }
        prefix = icons.get(status, "[*]")
        with self.lock:
            print(f"{prefix} {msg}")

    def print_progress(self):
        """Thread-safe progress bar"""
        with self.lock:
            elapsed = int(time.time() - self.start_time)
            total = self.total_tasks
            done = self.completed_tasks
            pct = min(100, int((done / total) * 100)) if total > 0 else 0

            if done > 0 and elapsed > 0:
                remaining = int((total - done) * (elapsed / done))
                eta = f"{remaining}s"
            else:
                eta = "..."

            bar_len = 25
            filled = int(bar_len * pct / 100)
            bar = "#" * filled + "-" * (bar_len - filled)

            print(f"\r[PROG] {bar} {pct}% | {done}/{total} | ETA: {eta}", end="")
            if pct == 100:
                print()

    # ======================== DNS ========================
    def dns_info(self):
        self.safe_print("DNS bilgileri aliniyor...", "scan")
        try:
            ip = socket.gethostbyname(self.target)
            self.results["dns"]["ip"] = ip
            self.safe_print(f"IP: {ip}", "success")

            try:
                hostname = socket.gethostbyaddr(ip)[0]
                self.results["dns"]["hostname"] = hostname
                self.safe_print(f"Hostname: {hostname}", "success")
            except:
                pass

            # DNS kayıtları (dnspython varsa)
            try:
                import dns.resolver
                records = {}
                for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
                    try:
                        answers = dns.resolver.resolve(self.target, rtype, lifetime=3)
                        records[rtype] = [str(r) for r in answers]
                    except:
                        pass
                self.results["dns"]["records"] = records
                for rtype, values in records.items():
                    self.safe_print(f"{rtype}: {', '.join(values[:3])}", "found")
            except ImportError:
                pass
            except Exception:
                pass

        except Exception as e:
            self.safe_print(f"DNS hatasi: {e}", "error")

        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== PORT TARAMA ========================
    def port_scan(self):
        self.safe_print("Portlar taranıyor (80+ port)...", "scan")

        ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 161, 443, 445, 465,
            514, 587, 631, 636, 873, 993, 995, 1080, 1099, 1352, 1433, 1521, 1723,
            2049, 2083, 2087, 2222, 2401, 3000, 3128, 3306, 3389, 3690, 4352,
            4443, 4646, 5000, 5001, 5222, 5223, 5432, 5544, 5555, 5666, 5800,
            5900, 5984, 6379, 7000, 7001, 7070, 7171, 7190, 7443, 7474, 7475,
            7777, 8000, 8001, 8008, 8080, 8081, 8088, 8090, 8091, 8092, 8123,
            8140, 8161, 8181, 8443, 8448, 8765, 8888, 9000, 9001, 9009, 9010,
            9042, 9090, 9092, 9100, 9151, 9160, 9200, 9300, 9418, 9999,
            10000, 11000, 11211, 20000, 27017, 28015, 29015, 30000, 32768
        ]

        open_ports = []

        def scan_port(p):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.5)
                result = sock.connect_ex((self.target, p))
                if result == 0:
                    banner = ""
                    try:
                        sock.settimeout(2)
                        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                        banner = sock.recv(256).decode('utf-8', errors='ignore').strip()
                    except:
                        pass
                    sock.close()
                    return (p, banner[:80] if banner else "Unknown")
                sock.close()
            except:
                pass
            return None

        with ThreadPoolExecutor(max_workers=8) as executor:  # 2. hata
            futures = [executor.submit(scan_port, p) for p in ports]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    port, banner = result
                    open_ports.append({"port": port, "banner": banner})
                    self.safe_print(f"Port {port} ACIK - {banner[:40]}", "found")

        self.results["ports"] = open_ports
        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== SSL ========================
    def ssl_analysis(self):
        self.safe_print("SSL sertifikasi analiz ediliyor...", "scan")
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=self.target) as s:
                s.settimeout(10)
                s.connect((self.target, 443))
                cert = s.getpeercert()
                cipher = s.cipher()

                self.results["ssl"] = {
                    "active": True,
                    "issuer": dict(x[0] for x in cert.get('issuer', [])),
                    "subject": dict(x[0] for x in cert.get('subject', [])),
                    "not_before": cert.get('notBefore', ''),
                    "not_after": cert.get('notAfter', ''),
                    "cipher": cipher[0] if cipher else '',
                    "protocol": s.version(),
                    "san": [x[1] for x in cert.get('subjectAltName', []) if x[0] == 'DNS']
                }
                self.safe_print(f"SSL Aktif - {cipher[0] if cipher else '?'}", "success")
        except:
            self.results["ssl"] = {"active": False}
            self.safe_print("SSL yok", "warning")

        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== HEADER ========================
    def header_analysis(self):
        self.safe_print("Header'lar analiz ediliyor...", "scan")

        for protocol in ["https", "http"]:
            try:
                r = self.session.get(f"{protocol}://{self.target}", timeout=5, verify=False)
                headers = dict(r.headers)
                self.results["headers"] = headers

                for key, value in headers.items():
                    self.safe_print(f"{key}: {value[:60]}", "found")

                cookies = r.cookies.get_dict()
                if cookies:
                    self.results["cookies"] = cookies
                    for name, value in cookies.items():
                        self.safe_print(f"Cookie: {name}={value[:20]}", "found")

                # WAF (header + body)
                waf = self.detect_waf(headers, r.text)
                if waf:
                    self.results["waf"] = waf
                    self.safe_print(f"WAF: {waf}", "warning")

                cloud = self.detect_cloud(headers)
                if cloud:
                    self.results["cloud"] = cloud
                    self.safe_print(f"Cloud: {cloud}", "found")

                break
            except:
                continue

        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    def detect_waf(self, headers, body=""):
        combined = str(headers).lower() + body.lower()
        for waf, sigs in self.waf_signatures.items():
            for sig in sigs:
                if sig.lower() in combined:
                    return waf
        return None

    def detect_cloud(self, headers):
        combined = str(headers).lower()
        for cloud, sigs in self.cloud_signatures.items():
            for sig in sigs:
                if sig.lower() in combined:
                    return cloud
        return None

    # ======================== TEKNOLOJİ ========================
    def tech_detect(self):
        self.safe_print("Teknolojiler tespit ediliyor...", "scan")

        techs = set()
        try:
            r = self.session.get(f"https://{self.target}", timeout=5, verify=False)
            content = r.text

            if "Server" in r.headers:
                techs.add(f"Server: {r.headers['Server']}")
            if "X-Powered-By" in r.headers:
                techs.add(f"Powered-By: {r.headers['X-Powered-By']}")

            for name, compiled in self.compiled_tech.items():
                if compiled.search(content) or compiled.search(str(r.headers)):
                    techs.add(name)
                    self.safe_print(f"Teknoloji: {name}", "found")

            self.results["technologies"] = list(techs)

        except Exception as e:
            self.safe_print(f"Tech detect hatasi: {e}", "warning")

        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== DİZİN TARAMA ========================
    def dir_scan(self):
        self.safe_print(f"Dizinler taranıyor ({len(self.dirs)} adet)...", "scan")

        def scan_dir(path):
            try:
                # Önce https, çalışmazsa http
                for protocol in ["https", "http"]:
                    try:
                        url = f"{protocol}://{self.target}{path}"
                        r = self.session.get(url, timeout=4, verify=False, allow_redirects=False)

                        if r.status_code in [200, 301, 302, 307, 401, 403, 405, 500]:
                            with self.lock:
                                self.results["directories"].append({
                                    "path": path,
                                    "status": r.status_code,
                                    "size": len(r.content),
                                    "server": r.headers.get("Server", ""),
                                    "content_type": r.headers.get("Content-Type", "")
                                })
                                self.found_items += 1
                                self.safe_print(f"{path} -> {r.status_code} ({len(r.content)}b)", "found")

                                # Dosya tespiti
                                if path.endswith(('.txt', '.json', '.xml', '.yml', '.yaml')):
                                    self.results["files"].append({"path": path, "type": "config"})

                                # Sadece ilgili durumlarda vuln/extra kontrol
                                if r.status_code in [200, 403, 500]:
                                    self.extract_info(r.text, url)
                                    self.check_vulnerability(url, r.text, r.headers)
                            break
                    except:
                        continue
            except:
                pass

            with self.lock:
                self.completed_tasks += 1
                self.print_progress()

        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(scan_dir, self.dirs)

        self.safe_print(f"{len(self.results['directories'])} dizin bulundu", "success")

    # ======================== SUBDOMAIN ========================
    def subdomain_scan(self):
        self.safe_print(f"Subdomain'ler taranıyor ({len(self.subdomains)} adet)...", "scan")

        found = []

        def scan_sub(sub):
            try:
                domain = f"{sub}.{self.target}"
                socket.setdefaulttimeout(2)
                socket.gethostbyname(domain)
                with self.lock:
                    found.append(domain)
                    self.safe_print(f"Subdomain: {domain}", "found")
            except:
                pass
            with self.lock:
                self.completed_tasks += 1
                self.print_progress()

        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(scan_sub, self.subdomains)

        self.results["subdomains"] = found
        self.safe_print(f"{len(found)} subdomain bulundu", "success")

    # ======================== VULN KONTROL ========================
    def check_vulnerability(self, url, content, headers):
        combined = (content + str(headers)).lower()

        for vuln_name, vuln_data in self.vuln_patterns.items():
            for compiled in vuln_data["compiled"]:
                if compiled.search(combined):
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "url": url,
                            "type": vuln_name,
                            "severity": vuln_data["severity"]
                        })
                        icon = "CRITICAL" if vuln_data["severity"] == "Critical" else "WARN"
                        self.safe_print(f"{icon} {vuln_name} TESPIT EDILDI! ({url})", "critical")
                    break

    # ======================== INFO EXTRACTION ========================
    def extract_info(self, content, url):
        # Email
        for email in self.email_re.findall(content)[:10]:
            if email not in self.results["emails"]:
                self.results["emails"].append(email)
                self.safe_print(f"Email: {email}", "found")

        # Link
        for link in self.link_re.findall(content)[:10]:
            if link not in self.results["links"]:
                self.results["links"].append(link)

        # Form
        if self.form_re.search(content):
            self.results["forms"].append(url)
            self.safe_print(f"Form bulundu: {url}", "found")

        # Parametre
        for param in self.param_re.findall(content)[:20]:
            if param not in self.results["parameters"]:
                self.results["parameters"].append(param)

        # JS
        for js in self.js_re.findall(content)[:10]:
            if js not in self.results["javascript"]:
                self.results["javascript"].append(js)

        # Yorum
        for comment in self.comment_re.findall(content)[:5]:
            if comment.strip():
                self.results["comments"].append(comment.strip()[:100])

    # ======================== RAPOR ========================
    def print_summary(self):
        elapsed = int(time.time() - self.start_time)

        print("\n" + "=" * 80)
        print(f"{BOLD}{C} TARAMA OZETI{N}")
        print("=" * 80)
        print(f"{Y}Süre:{N} {elapsed} saniye")
        print(f"{Y}Hedef:{N} {self.target}")
        print(f"{Y}Acik Port:{N} {len(self.results['ports'])}")
        print(f"{Y}Dizin:{N} {len(self.results['directories'])}")
        print(f"{Y}Guvenlik Acigi:{N} {len(self.results['vulnerabilities'])}")
        print(f"{Y}Subdomain:{N} {len(self.results['subdomains'])}")
        print(f"{Y}Teknoloji:{N} {len(self.results['technologies'])}")
        print(f"{Y}Email:{N} {len(self.results['emails'])}")
        print(f"{Y}Link:{N} {len(self.results['links'])}")
        print(f"{Y}Form:{N} {len(self.results['forms'])}")
        print(f"{Y}Parametre:{N} {len(self.results['parameters'])}")
        print(f"{Y}JavaScript:{N} {len(self.results['javascript'])}")
        print(f"{Y}Yorum:{N} {len(self.results['comments'])}")
        print("=" * 80)

        critical = [v for v in self.results['vulnerabilities'] if v['severity'] == 'Critical']
        if critical:
            print(f"\n{R}KRITIK GUVENLIK ACIKLARI:{N}")
            for v in critical:
                print(f"  [!] {v['type']} -> {v['url']}")

        if self.results['emails']:
            print(f"\n{C}EMAILLER:{N}")
            for email in self.results['emails'][:5]:
                print(f"  [>] {email}")

        interesting = [d for d in self.results['directories'] if d['status'] in [200, 403]]
        if interesting:
            print(f"\n{G}ONEMLI DIZINLER:{N}")
            for d in interesting[:10]:
                print(f"  [+] {d['path']} -> {d['status']}")

        print("=" * 80)

    def save_report(self):
        filename = f"scan_{self.target}_{int(time.time())}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        self.safe_print(f"Rapor kaydedildi: {filename}", "success")

    # ======================== MAIN SCAN ========================
    def full_scan(self):
        print(f"\n{BOLD}{M} ULTRA MEGA SCANNER FINAL BASLATILIYOR{N}")
        print(f"{B}Target: {self.target}{N}")
        print(f"{B}Baslangic: {datetime.now().strftime('%H:%M:%S')}{N}\n")

        self.print_progress()

        self.dns_info()
        self.port_scan()
        self.ssl_analysis()
        self.header_analysis()
        self.tech_detect()
        self.dir_scan()
        self.subdomain_scan()

        self.results["status"] = "Tamamlandi"
        with self.lock:
            self.completed_tasks = self.total_tasks
        self.print_progress()

        self.print_summary()

        if input("\nRaporu kaydet? (E/H): ").upper() == "E":
            self.save_report()


# ============================================================
# MAIN
# ============================================================
def main():
    print(f"""{BOLD}
╔═══════════════════════════════════════════════════════════╗
║  {C} ULTRA MEGA SCANNER FINAL{C}                             ║
║  {Y}47 HATA GIDERILDI - iSH UYUMLU{N}                         ║
╚═══════════════════════════════════════════════════════════╝
{N}""")

    target = input("Hedef (domain/IP): ").strip()
    if not target:
        target = "silvacheck.com"

    scanner = UltraMegaScanner(target)
    scanner.full_scan()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCikis yapiliyor...")
    except Exception as e:
        print(f"\n[R] Hata: {e}{N}")
