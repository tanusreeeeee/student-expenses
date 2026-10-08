"""Khata Guru core logic. No UI here. All models are open-weight and run locally."""
import json
import os
import sqlite3
from pathlib import Path
import tempfile
import datetime as dt

DB_PATH = str(Path(__file__).with_name("khata.db"))   # always next to this file, any OS
LLM_MODEL = os.getenv("KG_LLM_MODEL", "qwen2.5:3b")
WHISPER_SIZE = os.getenv("KG_WHISPER_SIZE", "small")   # "base" is faster on slow computers
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")   # local only

KINDS = ["credit_given", "payment_received", "cash_sale"]
# Nudges Whisper to write Hindi in English letters (Hinglish), which is easier to read in a ledger
WHISPER_HINT = "Ramesh ne 2 kilo sugar udhaar liya, 90 rupees. Suresh ne 500 rupees wapas diye."

SCHEMA = {
    "type": "object",
    "properties": {
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "customer": {"type": "string"},
                    "kind": {"type": "string", "enum": KINDS},
                    "item": {"type": "string"},
                    "amount": {"type": "number"},
                },
                "required": ["customer", "kind", "item", "amount"],
            },
        }
    },
    "required": ["entries"],
}

EXTRACT_PROMPT = """You turn a shopkeeper's spoken sentences into ledger entries.
Rules:
- kind = "credit_given" when the customer took goods and will pay later (udhaar, baaki, on credit).
- kind = "payment_received" when a customer paid back an earlier due.
- kind = "cash_sale" when goods were sold and paid immediately. Use customer "walk-in" if no name is said.
- amount is in rupees, as a number. If no amount is spoken, use 0.
- item is the goods (e.g. "2 kg sugar"). Use "" if none.
- One sentence can contain several entries. Do not invent anything that was not said.

Examples:
"Ramesh ne 2 kilo sugar udhaar liya, 90 rupees" -> customer Ramesh, credit_given, item "2 kg sugar", amount 90
"Suresh ne 500 wapas diye" -> customer Suresh, payment_received, item "", amount 500
"sold a biscuit packet for 20 rupees cash" -> customer walk-in, cash_sale, item "biscuit packet", amount 20
"""


# ---------- database ----------
def get_db(path=None):
    con = sqlite3.connect(path or DB_PATH)
    con.execute(
        """CREATE TABLE IF NOT EXISTS ledger(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, customer TEXT NOT NULL, kind TEXT NOT NULL,
            item TEXT, amount REAL NOT NULL)"""
    )
    return con


def save_entries(con, entries, when=None):
    ts = (when or dt.datetime.now()).isoformat(timespec="seconds")
    rows = [
        (ts, str(e["customer"]).strip().title(), e["kind"], e.get("item", ""), float(e["amount"]))
        for e in entries
        if e.get("kind") in KINDS and str(e.get("customer", "")).strip()
    ]
    con.executemany("INSERT INTO ledger(ts,customer,kind,item,amount) VALUES (?,?,?,?,?)", rows)
    con.commit()
    return len(rows)


def load_ledger(con):
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM ledger ORDER BY ts DESC", con)
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"])
    return df


# ---------- speech to text (Whisper, open-weight, runs locally) ----------
_whisper = None


def transcribe(audio_bytes, language=None):
    global _whisper
    from faster_whisper import WhisperModel
    if _whisper is None:
        _whisper = WhisperModel(WHISPER_SIZE, device="cpu", compute_type="int8")
    fd, path = tempfile.mkstemp(suffix=".wav")   # works on Windows, macOS and Linux
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(audio_bytes)
        segments, _ = _whisper.transcribe(
            path, language=language, vad_filter=True, beam_size=1,
            condition_on_previous_text=False, initial_prompt=WHISPER_HINT)
        return " ".join(seg.text.strip() for seg in segments).strip()
    finally:
        os.remove(path)


# ---------- LLM (Qwen via Ollama, open-weight, runs locally) ----------
def _client():
    import ollama
    return ollama.Client(host=OLLAMA_HOST)


def extract_entries(text):
    resp = _client().chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": text},
        ],
        format=SCHEMA,
        options={"temperature": 0},
        keep_alive="30m",
    )
    return clean_entries(json.loads(resp["message"]["content"]).get("entries", []))


# ---------- numbers are computed in Python, never by the LLM ----------
def balances(df):
    import pandas as pd
    if df.empty:
        return pd.DataFrame(columns=["customer", "owes"])
    d = df[df["kind"] != "cash_sale"].copy()
    d["signed"] = d["amount"].where(d["kind"] == "credit_given", -d["amount"])
    out = d.groupby("customer")["signed"].sum().reset_index(name="owes")
    return out[out["owes"] > 0].sort_values("owes", ascending=False).reset_index(drop=True)


def weekly_facts(df, today=None):
    today = today or dt.datetime.now()
    week = df[df["ts"] >= today - dt.timedelta(days=7)] if not df.empty else df
    bal = balances(df)
    oldest = {}
    if not df.empty:
        for name in bal["customer"]:
            c = df[(df["customer"] == name) & (df["kind"] == "credit_given")]
            if not c.empty:
                oldest[name] = int((today - c["ts"].min()).days)
    return {
        "credit_given_this_week": float(week.loc[week["kind"] == "credit_given", "amount"].sum()) if not week.empty else 0.0,
        "payments_received_this_week": float(week.loc[week["kind"] == "payment_received", "amount"].sum()) if not week.empty else 0.0,
        "cash_sales_this_week": float(week.loc[week["kind"] == "cash_sale", "amount"].sum()) if not week.empty else 0.0,
        "total_outstanding": float(bal["owes"].sum()) if not bal.empty else 0.0,
        "top_dues": [
            {"customer": r.customer, "owes": float(r.owes), "days_since_first_credit": oldest.get(r.customer, 0)}
            for r in bal.head(3).itertuples()
        ],
    }


def weekly_advice(facts, language="English"):
    prompt = (
        "You advise a small kirana shopkeeper in Bengaluru. Using ONLY the facts below "
        "(all numbers are already correct, do not recalculate or invent any), write 4 short, "
        "practical tips about collecting dues and managing credit. Use simple words. "
        f"Write in {language}. Mention customer names and rupee amounts exactly as given.\n\n"
        f"FACTS: {json.dumps(facts, ensure_ascii=False)}"
    )
    resp = _client().chat(model=LLM_MODEL, messages=[{"role": "user", "content": prompt}],
                       options={"temperature": 0.3}, keep_alive="30m")
    return resp["message"]["content"]


# ---------- helpers added for reliability ----------
def clean_entries(entries):
    out = []
    for e in entries:
        try:
            amt = abs(float(e.get("amount", 0)))
        except (TypeError, ValueError):
            amt = 0.0
        kind = e.get("kind") if e.get("kind") in KINDS else "credit_given"
        name = str(e.get("customer", "")).strip() or "Walk-in"
        out.append({"customer": name, "kind": kind, "item": str(e.get("item", "")).strip(), "amount": amt})
    return out


def describe(e, lang="en"):
    """One plain sentence so the shopkeeper can check an entry at a glance."""
    c, i, a, k = e.get("customer", "?"), e.get("item", ""), e.get("amount", 0), e.get("kind")
    a = f"₹{float(a):,.0f}"
    if lang == "hi":
        if k == "credit_given":
            return f"{c} ने {i or 'सामान'} उधार लिया, {a}"
        if k == "payment_received":
            return f"{c} ने {a} वापस दिए"
        return f"नकद बिक्री: {i or 'सामान'}, {a}"
    if k == "credit_given":
        return f"{c} took {i or 'goods'} on credit, {a}"
    if k == "payment_received":
        return f"{c} paid back {a}"
    return f"Cash sale: {i or 'goods'}, {a}"


def plain_summary(facts):
    """Rule-based summary. Works even if the AI model is unavailable."""
    lines = [
        f"This week: credit given ₹{facts['credit_given_this_week']:,.0f}, "
        f"payments received ₹{facts['payments_received_this_week']:,.0f}, "
        f"cash sales ₹{facts['cash_sales_this_week']:,.0f}.",
        f"Total still to collect: ₹{facts['total_outstanding']:,.0f}.",
    ]
    for d in facts["top_dues"]:
        lines.append(f"Chase {d['customer']}: owes ₹{d['owes']:,.0f} (first credit {d['days_since_first_credit']} days ago).")
    return lines


def clear_ledger(con):
    con.execute("DELETE FROM ledger")
    con.commit()


def health():
    """Checks used by the sidebar so you can see problems before the demo."""
    import importlib.util
    out = {"Whisper installed": importlib.util.find_spec("faster_whisper") is not None,
           "Ollama running": False, f"Model {LLM_MODEL} pulled": False}
    try:
        resp = _client().list()
        models = resp["models"] if isinstance(resp, dict) else resp.models
        names = []
        for m in models:
            n = m.get("model") or m.get("name") if isinstance(m, dict) else (getattr(m, "model", None) or getattr(m, "name", ""))
            names.append(n or "")
        out["Ollama running"] = True
        out[f"Model {LLM_MODEL} pulled"] = any(n.startswith(LLM_MODEL) for n in names)
    except Exception:
        pass
    return out
