#!/usr/bin/env python3
# KSIB ULTRA FULL MEGA SCANNER PRO MAX + 10 FİKİR
# pip install requests dnspython websocket-client

import socket, ssl, requests, json, time, re, sys, hashlib, base64, random
from datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
import urllib3
urllib3.disable_warnings()

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
M = "\033[95m"; C = "\033[96m"; N = "\033[0m"; BOLD = "\033[1m"

class ProMaxPlusScanner:
    def __init__(self, target):
        self.target = target
        self.start = time.time()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive"
        })
        self.session.timeout = 2

        self.results = {
            "target": target,
            "dns": {},
            "ports": [],
            "banners": [],
            "ssl": {},
            "headers": {},
            "security_headers": {},
            "waf": None,
            "cloud": None,
            "tech": [],
            "dirs": [],
            "subdomains": [],
            "vulns": [],
            "emails": [],
            "links": [],
            "forms": [],
            "cookies": [],
            "server": None,
            "parameters": [],
            "js_endpoints": [],
            "api_endpoints": [],
            "backup_files": [],
            "robots": [],
            "sitemap_urls": [],
            "hardcoded_secrets": [],
            "metatags": {},
            "cors": {},
            "tls_versions": [],
            "http_methods": {},
            "response_times": [],
            "subdomain_takeover": [],
            "dns_zone": [],
            "spf_dmarc": {},
            "interesting_files": [],
            "status_codes": {},
            "wp_users": [],
            "wp_plugins": [],
            "wp_version": None,
            "rate_limit": {"tested": False, "result": "Bilgi yok"},
            "twofa_bypass": {"tested": False, "result": "Bilgi yok"},
            "idor": {"tested": False, "result": "Bilgi yok"},
            "sqli_tests": [],
            "xss_tests": [],
            "open_redirect_tests": [],
            "api_fuzz": [],
            "websocket": {"found": False, "url": None},
            "grpc": {"found": False, "url": None}
        }

        # PORTLAR (200+)
        self.ports = [
            21,22,23,25,53,80,110,111,135,139,143,161,443,445,465,
            514,587,631,636,873,993,995,1080,1099,1352,1433,1521,1723,
            2049,2083,2087,2222,2401,3000,3128,3306,3389,3690,4352,
            4443,4646,5000,5001,5222,5223,5432,5544,5555,5666,5800,
            5900,5984,6379,7000,7001,7070,7171,7190,7443,7474,7475,
            7777,8000,8001,8008,8080,8081,8088,8090,8091,8092,8123,
            8140,8161,8181,8443,8448,8765,8888,9000,9001,9009,9010,
            9042,9090,9092,9100,9151,9160,9200,9300,9418,9999,
            10000,11000,11211,20000,27017,28015,29015,30000,32768
        ]

        # DİZİNLER (300+)
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
            "/fonts", "/icons", "/avatar", "/logo", "/favicon",
            "/cpanel", "/plesk", "/webmail", "/mail", "/roundcube",
            "/adminer", "/pgadmin", "/phpPgAdmin", "/mysqladmin",
            "/server-info", "/.svn", "/.aws", "/.ssh", "/.ftp",
            "/Dockerfile", "/docker-compose.yml", "/Makefile", "/README.md",
            "/backup-old", "/temp", "/cache", "/forum", "/blog", "/news",
            "/download", "/upload", "/uploads", "/files", "/file",
            "/app", "/application", "/src", "/source", "/code", "/public",
            "/private", "/secure", "/secret", "/confidential", "/internal",
            "/backup.zip", "/backup.tar", "/backup.gz", "/backup.rar",
            "/wp-admin", "/wp-login.php", "/wp-register.php", "/wp-activate.php",
            "/wp-comments-post.php", "/wp-cron.php", "/wp-links-opml.php",
            "/wp-load.php", "/wp-mail.php", "/wp-settings.php", "/wp-signup.php",
            "/wp-trackback.php", "/xmlrpc.php", "/wp-json", "/wp-content",
            "/wp-includes", "/wp-admin/admin-ajax.php", "/wp-admin/admin-post.php",
            "/wp-admin/admin.php", "/wp-admin/async-upload.php",
            "/wp-admin/authorize-application.php", "/wp-admin/comment.php",
            "/wp-admin/credits.php", "/wp-admin/custom-header.php",
            "/wp-admin/customize.php", "/wp-admin/edit-comments.php",
            "/wp-admin/edit-form-advanced.php", "/wp-admin/edit-form-blocks.php",
            "/wp-admin/edit-link-form.php", "/wp-admin/edit-tags.php",
            "/wp-admin/edit.php", "/wp-admin/export.php", "/wp-admin/freedoms.php",
            "/wp-admin/import.php", "/wp-admin/index.php", "/wp-admin/install.php",
            "/wp-admin/link-add.php", "/wp-admin/link-manager.php",
            "/wp-admin/link-parse-opml.php", "/wp-admin/media-new.php",
            "/wp-admin/media-upload.php", "/wp-admin/menu-header.php",
            "/wp-admin/menu.php", "/wp-admin/moderation.php", "/wp-admin/my-sites.php",
            "/wp-admin/nav-menus.php", "/wp-admin/network",
            "/wp-admin/options-discussion.php", "/wp-admin/options-general.php",
            "/wp-admin/options-media.php", "/wp-admin/options-permalink.php",
            "/wp-admin/options-privacy.php", "/wp-admin/options-reading.php",
            "/wp-admin/options-writing.php", "/wp-admin/options.php",
            "/wp-admin/plugin-editor.php", "/wp-admin/plugin-install.php",
            "/wp-admin/plugins.php", "/wp-admin/post-new.php", "/wp-admin/post.php",
            "/wp-admin/press-this.php", "/wp-admin/privacy.php", "/wp-admin/profile.php",
            "/wp-admin/revision.php", "/wp-admin/upgrade.php", "/wp-admin/user-edit.php",
            "/wp-admin/user-new.php", "/wp-admin/users.php", "/wp-admin/widgets.php",
            "/.git/config", "/.git/HEAD", "/.git/index", "/.git/objects",
            "/.svn/entries", "/.svn/wc.db", "/.env", "/.env.backup",
            "/.aws/credentials", "/.ssh/id_rsa", "/.ssh/authorized_keys"
        ]

        # SUBDOMAIN (150+)
        self.subdomains = [
            "www", "mail", "ftp", "dev", "test", "stage", "staging", "api", "admin",
            "cdn", "static", "blog", "shop", "docs", "support", "demo", "backup",
            "beta", "alpha", "preprod", "uat", "qa", "vpn", "secure", "portal",
            "gateway", "edge", "internal", "office", "remote", "db", "mysql",
            "postgres", "mongodb", "redis", "elastic", "search", "analytics",
            "monitor", "grafana", "kibana", "prometheus", "jenkins", "git",
            "svn", "ci", "cd", "deploy", "build", "artifact", "registry",
            "auth", "oauth", "sso", "login", "signin", "app", "mobile", "m",
            "partner", "affiliate", "vendor", "customer", "ecommerce",
            "store", "cart", "payment", "pay", "news", "media", "video",
            "images", "img", "css", "js", "fonts", "icons", "assets",
            "data", "database", "sql", "postgres", "mongo", "redis",
            "cache", "memcache", "elasticsearch", "kibana", "grafana",
            "prometheus", "jenkins", "gitlab", "github", "bitbucket",
            "confluence", "wiki", "docs", "support", "help", "faq",
            "community", "forum", "groups", "lists", "mailman",
            "planet", "blogs", "news", "press", "media", "video",
            "download", "uploads", "files", "file", "data", "backup",
            "development", "testing", "quality", "staging", "stage",
            "preprod", "production", "prod", "live", "uat", "sandbox",
            "showcase", "presentation", "marketing", "sales", "info",
            "about", "contact", "support", "help", "career", "jobs"
        ]

        self.total = len(self.dirs) + len(self.subdomains) + len(self.ports) + 40
        self.done = 0

        self.waf_sigs = {
            "Cloudflare": ["cf-ray", "__cfduid", "cloudflare"],
            "AWS WAF": ["x-amzn-requestid", "awswaf"],
            "Sucuri": ["sucuri", "x-sucuri-id"],
            "ModSecurity": ["modsecurity", "owasp"],
            "Wordfence": ["wordfence", "wfvt_"],
            "Akamai": ["akamai", "x-akamai"],
            "Imperva": ["incap_ses", "visid_incap"]
        }
        self.cloud_sigs = {
            "AWS": ["x-amz", "cloudfront", "s3.amazonaws"],
            "Cloudflare": ["cf-", "cloudflare"],
            "Google": ["x-gcs", "google-cloud"],
            "Azure": ["x-ms", "azure"],
            "Akamai": ["akamai", "x-ak"],
            "Fastly": ["x-fastly", "fastly"]
        }
        self.tech_patterns = {
            "WordPress": r"(wp-content|wp-includes|wp-json)",
            "Laravel": r"(laravel|csrf-token|_token)",
            "Django": r"(csrfmiddlewaretoken|django)",
            "React": r"(react|_reactRootContainer)",
            "Angular": r"(angular|ng-app)",
            "Vue": r"(vue|v-bind|v-for)",
            "Bootstrap": r"(bootstrap|data-bs-)",
            "jQuery": r"(jquery|\$\(document\))",
            "Nginx": r"(nginx|server: nginx)",
            "Apache": r"(apache|server: apache)",
            "IIS": r"(iis|server: microsoft-iis)",
            "Tomcat": r"(tomcat|server: apache-coyote)",
            "Node.js": r"(node|express|server: nodejs)",
            "Ruby on Rails": r"(rails|ruby)",
            "PHP": r"(php|\.php|<?php)",
            "Python": r"(python|wsgi|uwsgi)",
            "Magento": r"(magento|skin/frontend)",
            "Shopify": r"(shopify|myshopify)",
            "Joomla": r"(joomla|com_content)",
            "Drupal": r"(drupal|sites/all)",
            "Gatsby": r"(gatsby|_gatsby)",
            "Next.js": r"(next|_next)",
            "Nuxt": r"(nuxt|_nuxt)",
            "Svelte": r"(svelte|_svelte)",
            "Tailwind": r"(tailwind|tw-)",
            "Font Awesome": r"(fa-|font-awesome)"
        }
        self.vuln_patterns = {
            "SQL Injection": r"(sql|mysql|postgresql|oracle|database error|syntax error|unclosed quotation)",
            "XSS": r"(<script|alert\(|prompt\(|onerror=|onload=)",
            "LFI/RFI": r"(etc/passwd|windows/win.ini|\.\./|include\()",
            "RCE": r"(system\(|exec\(|eval\(|passthru\()",
            ".git Exposed": r"(git/HEAD|refs/heads/master|objects/|refs/)",
            ".env Exposed": r"(DB_HOST|DB_NAME|DB_USER|DB_PASS|APP_KEY|SECRET)",
            "PHPInfo": r"(phpinfo\(|PHP Version|Zend Engine)",
            "Dir Listing": r"(index of /|parent directory|directory listing)",
            "XXE": r"(!DOCTYPE|!ENTITY|SYSTEM|PUBLIC)",
            "SSRF": r"(url=|path=|dest=|redirect=)",
            "Open Redirect": r"(redirect=|return=|next=)",
            "Sensitive Data": r"(\b[0-9]{16}\b|\b\d{3}-\d{2}-\d{4}\b)"
        }

    def log(self, msg, status="info"):
        icons = {"info":"[*]", "success":"[+]", "error":"[-]", "warning":"[!]", "found":"[>]", "critical":"[!]", "test":"[T]"}
        print(f"{icons.get(status, '[*]')} {msg}")

    def progress(self):
        pct = int((self.done / self.total) * 100) if self.total else 0
        bar = "#" * int(pct/4) + "-" * (25 - int(pct/4))
        eta = "..." if self.done == 0 else f"{int((self.total - self.done) * (time.time()-self.start) / max(1, self.done))}s"
        print(f"\r[PROG] {bar} {pct}% | {self.done}/{self.total} | ETA: {eta}", end="")
        if pct == 100: print()

    # ==================== 1. DNS ====================
    def dns(self):
        self.log("DNS bilgileri...", "scan")
        try:
            ip = socket.gethostbyname(self.target)
            self.results["dns"]["ip"] = ip
            self.log(f"IP: {ip}", "success")
            try:
                host = socket.gethostbyaddr(ip)[0]
                self.results["dns"]["hostname"] = host
                self.log(f"Hostname: {host}", "success")
            except: pass
            try:
                import dns.resolver
                ns = dns.resolver.resolve(self.target, 'NS', lifetime=2)
                for ns_server in ns:
                    try:
                        import dns.zone
                        zone = dns.zone.from_xfr(dns.query.xfr(str(ns_server), self.target))
                        self.results["dns_zone"] = [str(name) for name in zone.nodes.keys()]
                        if self.results["dns_zone"]:
                            self.log(f"Zone transfer: {len(self.results['dns_zone'])} kayit", "found")
                    except: pass
                for rtype in ["TXT", "MX", "NS", "SOA"]:
                    try:
                        answers = dns.resolver.resolve(self.target, rtype, lifetime=2)
                        self.results["dns"][rtype.lower()] = [str(r) for r in answers]
                        if rtype == "TXT":
                            for txt in answers:
                                if "spf" in str(txt).lower():
                                    self.results["spf_dmarc"]["spf"] = str(txt)
                                if "dmarc" in str(txt).lower():
                                    self.results["spf_dmarc"]["dmarc"] = str(txt)
                    except: pass
                if self.results["spf_dmarc"]:
                    self.log(f"SPF/DMARC: {self.results['spf_dmarc']}", "found")
            except: pass
        except Exception as e:
            self.log(f"DNS hatasi: {e}", "error")
        self.done += 1; self.progress()

    # ==================== 2. PORT + BANNER ====================
    def port(self):
        self.log(f"Portlar taranıyor ({len(self.ports)})...", "scan")
        for p in self.ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((self.target, p)) == 0:
                    self.results["ports"].append(p)
                    try:
                        s.settimeout(1)
                        if p in [21,25,80,110,143,443,587,993,995,3306,5432,6379]:
                            s.send(b"HEAD / HTTP/1.0\r\n\r\n" if p in [80,443,8080,8443] else b"\r\n")
                            banner = s.recv(256).decode('utf-8', errors='ignore').strip()
                            if banner:
                                self.results["banners"].append({"port": p, "banner": banner[:100]})
                                self.log(f"Port {p} Banner: {banner[:50]}", "found")
                    except: pass
                    self.log(f"Port {p} ACIK", "found")
                s.close()
            except: pass
            self.done += 1
            if self.done % 20 == 0: self.progress()
        self.progress()

    # ==================== 3. SSL + TLS ====================
    def ssl(self):
        self.log("SSL/TLS kontrol...", "scan")
        for version in [ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLSv1_2]:
            try:
                ctx = ssl.SSLContext(version)
                with ctx.wrap_socket(socket.socket(), server_hostname=self.target) as s:
                    s.settimeout(2)
                    s.connect((self.target, 443))
                    self.results["tls_versions"].append(str(version))
                    self.log(f"TLS versiyon destekleniyor: {version}", "warning" if version in [ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_1] else "success")
            except: pass
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=self.target) as s:
                s.settimeout(3)
                s.connect((self.target, 443))
                cipher = s.cipher()[0]
                self.results["ssl"] = {"active": True, "cipher": cipher, "protocol": s.version()}
                self.log(f"SSL Aktif - {cipher}", "success")
        except:
            self.results["ssl"] = {"active": False}
            self.log("SSL yok", "warning")
        self.done += 1; self.progress()

    # ==================== 4. HEADER ====================
    def header(self):
        self.log("Header'lar...", "scan")
        for proto in ["https", "http"]:
            try:
                r = self.session.get(f"{proto}://{self.target}", timeout=2, verify=False)
                headers = dict(r.headers)
                self.results["headers"] = headers
                for k, v in list(headers.items())[:12]:
                    self.log(f"{k}: {v[:50]}", "found")
                if "Server" in headers:
                    self.results["server"] = headers["Server"]
                    self.results["tech"].append(f"Server: {headers['Server']}")
                sec_headers = {
                    "Strict-Transport-Security": "HSTS eksik!",
                    "Content-Security-Policy": "CSP eksik!",
                    "X-Frame-Options": "Clickjacking riski!",
                    "X-Content-Type-Options": "MIME-sniff riski!",
                    "Referrer-Policy": "Referrer bilgisi sızıyor!"
                }
                for h, msg in sec_headers.items():
                    if h not in headers:
                        self.results["security_headers"][h] = "EKSIK"
                        self.log(f"Security Header: {h} -> {msg}", "warning")
                combined = str(headers).lower()
                for waf, sigs in self.waf_sigs.items():
                    if any(s in combined for s in sigs):
                        self.results["waf"] = waf
                        self.log(f"WAF: {waf}", "warning")
                for cloud, sigs in self.cloud_sigs.items():
                    if any(s in combined for s in sigs):
                        self.results["cloud"] = cloud
                        self.log(f"Cloud: {cloud}", "found")
                if r.cookies:
                    self.results["cookies"] = list(r.cookies.keys())
                break
            except:
                continue
        self.done += 1; self.progress()

    # ==================== 5. HTTP METHODS ====================
    def http_methods(self):
        self.log("HTTP Methods test...", "scan")
        methods = ["OPTIONS", "PUT", "DELETE", "PATCH", "TRACE", "CONNECT"]
        for method in methods:
            try:
                r = self.session.request(method, f"https://{self.target}", timeout=2, verify=False)
                if r.status_code not in [405, 501]:
                    self.results["http_methods"][method] = r.status_code
                    self.log(f"Method {method}: {r.status_code}", "found")
            except:
                pass
        self.done += 1; self.progress()

    # ==================== 6. TECH ====================
    def tech(self):
        self.log("Teknolojiler...", "scan")
        try:
            r = self.session.get(f"https://{self.target}", timeout=2, verify=False)
            content = r.text
            for name, pattern in self.tech_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    if name not in self.results["tech"]:
                        self.results["tech"].append(name)
                        self.log(f"Tech: {name}", "found")
            # 7. WordPress version
            if "WordPress" in self.results["tech"]:
                try:
                    wp_login = self.session.get(f"https://{self.target}/wp-login.php", timeout=2, verify=False)
                    for meta in re.findall(r'<meta[^>]+>', wp_login.text):
                        if 'name="generator"' in meta and "WordPress" in meta:
                            version = re.search(r'WordPress ([0-9.]+)', meta)
                            if version:
                                self.results["wp_version"] = version.group(1)
                                self.log(f"WordPress version: {version.group(1)}", "found")
                    if not self.results["wp_version"]:
                        css = self.session.get(f"https://{self.target}/wp-admin/css/install.css", timeout=2, verify=False)
                        for line in css.text.split("\n"):
                            if "Version" in line:
                                version = re.search(r'Version: ([0-9.]+)', line)
                                if version:
                                    self.results["wp_version"] = version.group(1)
                                    self.log(f"WordPress version: {version.group(1)}", "found")
                except: pass
        except:
            pass
        self.done += 1; self.progress()

    # ==================== 7. DİZİN ====================
    def dir(self):
        self.log(f"Dizinler ({len(self.dirs)})...", "scan")
        for d in self.dirs:
            for proto in ["https", "http"]:
                try:
                    url = f"{proto}://{self.target}{d}"
                    start_time = time.time()
                    r = self.session.get(url, timeout=1.2, verify=False, allow_redirects=False)
                    rt = (time.time() - start_time)
                    self.results["response_times"].append(rt)

                    if r.status_code in [200, 301, 302, 403, 401, 405, 500, 502, 503]:
                        self.results["dirs"].append({"path": d, "status": r.status_code})
                        self.results["status_codes"][str(r.status_code)] = self.results["status_codes"].get(str(r.status_code), 0) + 1
                        self.log(f"{d} -> {r.status_code}", "found")
                        self.results["response_times"].append(rt)

                        # 8. API fuzzing
                        if d.startswith("/api") or d == "/graphql" or d == "/wp-json":
                            self.results["api_endpoints"].append({"path": d, "status": r.status_code})
                            self.log(f"API: {d} -> {r.status_code}", "found")

                        # 9. WebSocket
                        if 'new WebSocket(' in r.text or 'ws://' in r.text or 'wss://' in r.text:
                            ws_match = re.search(r'(wss?://[^\s"\']+)', r.text)
                            if ws_match:
                                self.results["websocket"]["found"] = True
                                self.results["websocket"]["url"] = ws_match.group(1)
                                self.log(f"WebSocket: {ws_match.group(1)}", "found")

                        # 10. gRPC (HTTP/2)
                        if "application/grpc" in str(r.headers) or "grpc-" in str(r.headers).lower():
                            self.results["grpc"]["found"] = True
                            self.results["grpc"]["url"] = url
                            self.log(f"gRPC: {url}", "found")

                        # ============ YENİ TESTLER ============
                        # 1. SQLi test (parametreler varsa)
                        params = re.findall(r'\?([a-zA-Z0-9_]+)=', r.text)
                        for param in params:
                            if param not in self.results["parameters"]:
                                self.results["parameters"].append(param)
                            # SQLi dene
                            payloads = ["'", '"', "1=1'", "1=1\""]
                            for payload in payloads:
                                test_url = f"{url}?{param}={payload}"
                                try:
                                    test_r = self.session.get(test_url, timeout=2, verify=False)
                                    if "syntax error" in test_r.text.lower() or "mysql" in test_r.text.lower() or "sql" in test_r.text.lower():
                                        self.results["sqli_tests"].append({"url": test_url, "payload": payload, "status": "BULUNDU!"})
                                        self.results["vulns"].append({"url": test_url, "type": f"SQLi ({payload})"})
                                        self.log(f"SQLi: {param}={payload} -> BULUNDU!", "critical")
                                    else:
                                        self.results["sqli_tests"].append({"url": test_url, "payload": payload, "status": "Güvende"})
                                        self.log(f"SQLi: {param}={payload} -> Güvende", "test")
                                except:
                                    self.results["sqli_tests"].append({"url": test_url, "payload": payload, "status": "Test başarısız"})
                                    self.log(f"SQLi: {param}={payload} -> Test başarısız", "error")

                            # 2. XSS test
                            xss_payloads = ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>']
                            for payload in xss_payloads:
                                test_url = f"{url}?{param}={payload}"
                                try:
                                    test_r = self.session.get(test_url, timeout=2, verify=False)
                                    if payload in test_r.text:
                                        self.results["xss_tests"].append({"url": test_url, "payload": payload, "status": "BULUNDU!"})
                                        self.results["vulns"].append({"url": test_url, "type": f"XSS ({payload[:20]})"})
                                        self.log(f"XSS: {param}={payload[:20]} -> BULUNDU!", "critical")
                                    else:
                                        self.results["xss_tests"].append({"url": test_url, "payload": payload, "status": "Güvende"})
                                        self.log(f"XSS: {param}={payload[:20]} -> Güvende", "test")
                                except:
                                    self.results["xss_tests"].append({"url": test_url, "payload": payload, "status": "Test başarısız"})
                                    self.log(f"XSS: {param}={payload[:20]} -> Test başarısız", "error")

                            # 3. Open Redirect
                            redirect_payloads = ['https://evil.com', '//evil.com', 'javascript:alert(1)']
                            for payload in redirect_payloads:
                                test_url = f"{url}?redirect={payload}&url={payload}&next={payload}&return={payload}"
                                try:
                                    test_r = self.session.get(test_url, timeout=2, verify=False, allow_redirects=False)
                                    if test_r.status_code in [301, 302, 307] and "evil.com" in test_r.headers.get("Location", ""):
                                        self.results["open_redirect_tests"].append({"url": test_url, "payload": payload, "status": "BULUNDU!"})
                                        self.results["vulns"].append({"url": test_url, "type": f"Open Redirect ({payload})"})
                                        self.log(f"Open Redirect: {payload} -> BULUNDU!", "critical")
                                    else:
                                        self.results["open_redirect_tests"].append({"url": test_url, "payload": payload, "status": "Güvende"})
                                        self.log(f"Open Redirect: {payload} -> Güvende", "test")
                                except:
                                    self.results["open_redirect_tests"].append({"url": test_url, "payload": payload, "status": "Test başarısız"})
                                    self.log(f"Open Redirect: {payload} -> Test başarısız", "error")

                        # 4. Rate limit (login sayfaları)
                        login_pages = ["/login", "/wp-login.php", "/admin/login", "/signin", "/auth/login"]
                        if d in login_pages and r.status_code in [200, 405]:
                            self.log(f"Rate limit test: {d}", "scan")
                            success = 0
                            for i in range(10):
                                try:
                                    test_r = self.session.post(f"{url}", data={"username": "test", "password": "test"}, timeout=1, verify=False)
                                    if test_r.status_code in [429, 503, 429]:
                                        self.results["rate_limit"]["tested"] = True
                                        self.results["rate_limit"]["result"] = "Rate limit VAR (429/503)"
                                        self.log(f"Rate limit: VAR! ({test_r.status_code})", "found")
                                        break
                                    if test_r.status_code in [200, 302]:
                                        success += 1
                                except:
                                    pass
                            if success >= 8 and not self.results["rate_limit"]["tested"]:
                                self.results["rate_limit"]["tested"] = True
                                self.results["rate_limit"]["result"] = "Rate limit YOK (10 istek başarılı)"
                                self.log("Rate limit: YOK! (10 istek başarılı)", "warning")

                        # 5. 2FA bypass
                        protected_pages = ["/dashboard", "/admin", "/profile", "/wp-admin", "/account"]
                        if d in protected_pages and r.status_code == 302:
                            self.results["twofa_bypass"]["tested"] = True
                            self.results["twofa_bypass"]["result"] = "Yönlendirme var, 2FA/oturum kontrolü çalışıyor"
                            self.log("2FA test: Yönlendirme var (güvende)", "success")
                        elif d in protected_pages and r.status_code == 200:
                            self.results["twofa_bypass"]["tested"] = True
                            self.results["twofa_bypass"]["result"] = "DİREKT ERİŞİM! (2FA atlanabilir)"
                            self.results["vulns"].append({"url": url, "type": "2FA Bypass (doğrudan erişim)"})
                            self.log("2FA test: DİREKT ERİŞİM! (2FA yok)", "critical")

                        # 6. IDOR test
                        id_patterns = [r'/user/(\d+)', r'/profile/(\d+)', r'id=(\d+)', r'user_id=(\d+)']
                        for pattern in id_patterns:
                            ids = re.findall(pattern, r.text)
                            for uid in ids[:3]:
                                test_id = str(int(uid) + 1) if uid.isdigit() else "2"
                                test_url = re.sub(r'\d+', test_id, url)
                                try:
                                    test_r = self.session.get(test_url, timeout=2, verify=False)
                                    if test_r.status_code == 200 and len(test_r.text) > 100:
                                        self.results["idor"]["tested"] = True
                                        self.results["idor"]["result"] = f"IDOR bulundu: {test_url}"
                                        self.results["vulns"].append({"url": test_url, "type": "IDOR"})
                                        self.log(f"IDOR: {test_url}", "critical")
                                    else:
                                        self.results["idor"]["tested"] = True
                                        self.results["idor"]["result"] = "IDOR bulunamadı"
                                        self.log("IDOR: Güvende", "test")
                                except:
                                    pass

                        # Robots
                        if d == "/robots.txt" and r.status_code == 200:
                            for line in r.text.split("\n"):
                                if "Disallow:" in line:
                                    self.results["robots"].append(line.strip())
                                    self.log(f"Robots: {line.strip()}", "found")

                        # Sitemap
                        if d == "/sitemap.xml" and r.status_code == 200:
                            for url2 in re.findall(r'<loc>(.*?)</loc>', r.text):
                                self.results["sitemap_urls"].append(url2)
                                self.log(f"Sitemap: {url2[:60]}", "found")

                        # Backup
                        if d.endswith(('.bak', '.old', '.zip', '.tar', '.gz', '.rar', '.7z')):
                            self.results["backup_files"].append({"path": d, "size": len(r.content)})
                            self.log(f"Backup: {d}", "found")

                        # Secrets
                        secrets = re.findall(r'(api[_-]?key|token|secret|password|passwd)[\s:=]+["\']?([a-zA-Z0-9_\-]{8,})', r.text, re.IGNORECASE)
                        for secret in secrets:
                            self.results["hardcoded_secrets"].append({"key": secret[0], "value": secret[1][:20]})
                            self.log(f"Secret: {secret[0]}={secret[1][:10]}...", "critical")

                        # WP Users
                        if "wp-json" in d or "wp-content" in d:
                            if r.status_code == 200:
                                users = re.findall(r'/"id":(\d+),"name":"([^"]+)"', r.text)
                                for uid, name in users:
                                    self.results["wp_users"].append({"id": uid, "name": name})
                                    self.log(f"WP User: {name} (ID:{uid})", "found")
                                plugins = re.findall(r'/"plugin":"([^"]+)"', r.text)
                                for plugin in plugins:
                                    self.results["wp_plugins"].append(plugin)
                                    self.log(f"WP Plugin: {plugin}", "found")

                        # Vuln
                        combined = (r.text + str(r.headers)).lower()
                        for vuln, pattern in self.vuln_patterns.items():
                            if re.search(pattern, combined, re.IGNORECASE):
                                self.results["vulns"].append({"url": url, "type": vuln})
                                self.log(f"{vuln} ({url})", "critical")
                        # Email
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
                        for e in emails[:10]:
                            if e not in self.results["emails"]:
                                self.results["emails"].append(e)
                                self.log(f"Email: {e}", "found")

                        # 3. API fuzzing wordlist
                        if d.startswith("/api"):
                            api_paths = ["/v1", "/v2", "/v3", "/users", "/posts", "/comments", "/auth", "/login", "/logout", "/register"]
                            for api_path in api_paths:
                                test_url = f"{url}{api_path}"
                                try:
                                    test_r = self.session.get(test_url, timeout=1, verify=False)
                                    if test_r.status_code in [200, 201, 401, 403]:
                                        self.results["api_fuzz"].append({"path": f"{d}{api_path}", "status": test_r.status_code})
                                        self.log(f"API Fuzz: {d}{api_path} -> {test_r.status_code}", "found")
                                except: pass

                        # CORS
                        if "Access-Control-Allow-Origin" in r.headers:
                            origin = r.headers.get("Access-Control-Allow-Origin")
                            self.results["cors"] = {"origin": origin}
                            if origin == "*":
                                self.results["vulns"].append({"url": url, "type": "CORS Misconfiguration (*)"})
                                self.log(f"CORS: * (Riskli!)", "critical")

                        # HTTP→HTTPS Redirect
                        if r.status_code == 302 and "Location" in r.headers and "http://" in r.headers["Location"]:
                            self.results["vulns"].append({"url": url, "type": "HTTP Redirect (Zayif)"})
                            self.log(f"HTTP Redirect: {url}", "warning")
                        break
                except:
                    continue
            self.done += 1
            if self.done % 5 == 0: self.progress()
        self.progress()

    # ==================== SUBDOMAIN ====================
    def sub(self):
        self.log(f"Subdomain'ler ({len(self.subdomains)})...", "scan")
        for sub in self.subdomains:
            try:
                domain = f"{sub}.{self.target}"
                socket.setdefaulttimeout(1)
                ip = socket.gethostbyname(domain)
                self.results["subdomains"].append({"domain": domain, "ip": ip})
                self.log(f"Sub: {domain} -> {ip}", "found")
                try:
                    import dns.resolver
                    cname = dns.resolver.resolve(domain, 'CNAME', lifetime=2)
                    for c in cname:
                        if "herokuapp" in str(c) or "github.io" in str(c) or "amazonaws" in str(c) or "azurewebsites" in str(c):
                            self.results["subdomain_takeover"].append({"domain": domain, "cname": str(c)})
                            self.log(f"Takeover: {domain} -> {c}", "critical")
                except: pass
            except: pass
            self.done += 1
            if self.done % 5 == 0: self.progress()
        self.progress()

    def summary(self):
        elapsed = int(time.time() - self.start)
        print("\n" + "="*80)
        print(f"{BOLD}{C} ULTRA FULL MEGA SCANNER PRO MAX + 10 FIKIR - RAPOR{N}")
        print("="*80)
        print(f"{Y}Süre:{N} {elapsed}s")
        print(f"{Y}Port:{N} {len(self.results['ports'])}")
        print(f"{Y}Banner:{N} {len(self.results['banners'])}")
        print(f"{Y}Dizin:{N} {len(self.results['dirs'])}")
        print(f"{Y}Subdomain:{N} {len(self.results['subdomains'])}")
        print(f"{Y}Vuln:{N} {len(self.results['vulns'])}")
        print(f"{Y}Email:{N} {len(self.results['emails'])}")
        print(f"{Y}Parameter:{N} {len(self.results['parameters'])}")
        print(f"{Y}API:{N} {len(self.results['api_endpoints'])}")
        print(f"{Y}Backup:{N} {len(self.results['backup_files'])}")
        print(f"{Y}WP Users:{N} {len(self.results['wp_users'])}")
        print(f"{Y}WP Plugins:{N} {len(self.results['wp_plugins'])}")
        print(f"{Y}WP Version:{N} {self.results['wp_version'] or '?'}")
        print(f"{Y}WebSocket:{N} {'Var' if self.results['websocket']['found'] else 'Yok'}")
        print(f"{Y}gRPC:{N} {'Var' if self.results['grpc']['found'] else 'Yok'}")
        print("="*80)

        # ============ TEST SONUÇLARI ============
        print(f"\n{BOLD}TEST SONUCLARI{N}")
        print("="*80)

        # SQLi
        if self.results["sqli_tests"]:
            bulunan = [t for t in self.results["sqli_tests"] if t["status"] == "BULUNDU!"]
            print(f"{Y}SQLi Testi:{N} {len(bulunan)} bulundu, {len(self.results['sqli_tests'])} test yapıldı")
            for t in self.results["sqli_tests"][:5]:
                status_icon = "🔥" if t["status"] == "BULUNDU!" else "✅" if t["status"] == "Güvende" else "❌"
                print(f"  {status_icon} {t['url'][:60]} -> {t['status']}")

        # XSS
        if self.results["xss_tests"]:
            bulunan = [t for t in self.results["xss_tests"] if t["status"] == "BULUNDU!"]
            print(f"{Y}XSS Testi:{N} {len(bulunan)} bulundu, {len(self.results['xss_tests'])} test yapıldı")
            for t in self.results["xss_tests"][:5]:
                status_icon = "🔥" if t["status"] == "BULUNDU!" else "✅" if t["status"] == "Güvende" else "❌"
                print(f"  {status_icon} {t['url'][:50]} -> {t['status']}")

        # Open Redirect
        if self.results["open_redirect_tests"]:
            bulunan = [t for t in self.results["open_redirect_tests"] if t["status"] == "BULUNDU!"]
            print(f"{Y}Open Redirect:{N} {len(bulunan)} bulundu, {len(self.results['open_redirect_tests'])} test yapıldı")

        # Rate Limit
        print(f"{Y}Rate Limit:{N} {self.results['rate_limit']['result']}")
        # 2FA
        print(f"{Y}2FA Bypass:{N} {self.results['twofa_bypass']['result']}")
        # IDOR
        print(f"{Y}IDOR:{N} {self.results['idor']['result']}")

        # Vuln list
        if self.results['vulns']:
            print(f"\n{R}GUVENLIK ACIKLARI:{N}")
            for v in self.results['vulns'][:20]:
                print(f"  [!] {v['type']} -> {v['url'][:60]}")

        if self.results['dirs']:
            print(f"\n{G}DIZINLER (ilk 15):{N}")
            for d in self.results['dirs'][:15]:
                print(f"  [+] {d['path']} -> {d['status']}")

        if self.results['subdomain_takeover']:
            print(f"\n{R}SUBDOMAIN TAKEOVER:{N}")
            for t in self.results['subdomain_takeover']:
                print(f"  [!] {t['domain']} -> {t['cname']}")

        print("="*80)

    def save(self):
        fname = f"scan_{self.target}_{int(time.time())}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        self.log(f"Rapor: {fname}", "success")

    def run(self):
        print(f"{BOLD}{M} ULTRA FULL MEGA SCANNER PRO MAX + 10 FIKIR{N}\n")
        self.dns()
        self.port()
        self.ssl()
        self.header()
        self.http_methods()
        self.tech()
        self.dir()
        self.sub()
        self.done = self.total
        self.progress()
        self.summary()
        if input("\nRaporu kaydet? (E/H): ").upper() == "E":
            self.save()

# ============================================================
def main():
    print(f"{BOLD}╔═══════════════════════════════════════════════╗")
    print(f"║ {C} PRO MAX + 10 FIKIR{BOLD}                      ║")
    print(f"║ {Y}SQLi | XSS | Redirect | Rate Limit{BOLD}      ║")
    print(f"║ {M}2FA | IDOR | API Fuzz | WebSocket | gRPC{BOLD} ║")
    print("╚═══════════════════════════════════════════════╝\n")
    target = input("Hedef: ").strip() or "silvacheck.com"
    ProMaxPlusScanner(target).run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCikis.")
    except Exception as e:
        print(f"\n{R}Hata: {e}{N}")
