"""
Haqqi — chat UI + live case-file card (Arabic, right-to-left).
Run (with the API running):  streamlit run ui/streamlit_app.py
"""
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="حقّي · Haqqi", page_icon="⚖️", layout="wide")

STATUS_AR = {"terminated": "تم فصله", "resigned": "استقال",
             "employed": "على رأس العمل", "seeking": "يبحث عن عمل"}
LABELS = {
    "role": "المسمى الوظيفي", "tenure_years": "مدة الخدمة (سنوات)",
    "monthly_salary": "الراتب الشهري (ريال)", "employment_status": "الحالة",
    "issue": "المشكلة", "contract_type": "نوع العقد",
    "notice_given": "الإشعار المُقدَّم", "termination_reason": "السبب المذكور",
}
EXAMPLES = [
    "فصلني صاحب العمل بعد ٤ سنوات، هل أستحق مكافأة نهاية الخدمة؟",
    "عقدي يمنعني من العمل لدى أي منافس لمدة ٥ سنوات، هل هذا نظامي؟",
    "أعمل ساعات إضافية دون أجر إضافي، ما حقوقي؟",
]

# ──────────────────────────────────────────────────────────────────────────────
# Design system: tokens + component styling, injected once.
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');

:root {
  --bg:        oklch(1 0 0);
  --surface:   oklch(0.986 0.006 165);
  --surface-2: oklch(0.972 0.009 165);
  --border:    oklch(0.905 0.012 165);
  --border-2:  oklch(0.86 0.014 165);
  --ink:       oklch(0.26 0.022 168);
  --body:      oklch(0.34 0.016 178);
  --muted:     oklch(0.47 0.013 178);
  --brand:     oklch(0.49 0.103 155);
  --brand-700: oklch(0.43 0.108 153);
  --brand-tint:oklch(0.965 0.03 160);
  --warn:      oklch(0.66 0.135 66);
  --warn-tint: oklch(0.965 0.045 78);
  --warn-ink:  oklch(0.46 0.10 58);
  --radius: 16px;
  --radius-sm: 11px;
  --shadow: 0 1px 2px oklch(0.4 0.03 165 / .05), 0 6px 20px oklch(0.4 0.03 165 / .06);
  --ease: cubic-bezier(.22,1,.36,1);
}

html, body, [data-testid="stAppViewContainer"], .stApp,
[data-testid="stChatInput"] textarea, input, button, textarea {
  font-family: 'IBM Plex Sans Arabic', system-ui, sans-serif !important;
}
.stApp { direction: rtl; background: var(--bg); color: var(--body); }
[data-testid="stMarkdownContainer"] { direction: rtl; text-align: right; }
[data-testid="stMarkdownContainer"] p { color: var(--body); line-height: 1.85; }

/* hide default chrome for a product feel */
#MainMenu, header[data-testid="stHeader"], footer { display: none; }
[data-testid="stAppViewContainer"] > .main .block-container {
  padding-top: 1.4rem; padding-bottom: 6rem; max-width: 1180px;
}

/* ── brand header ─────────────────────────────────────────────── */
.hq-top { display:flex; align-items:center; gap:.85rem; }
.hq-mark {
  width:46px; height:46px; border-radius:13px; flex:0 0 auto;
  background: linear-gradient(155deg, var(--brand), var(--brand-700));
  display:grid; place-items:center; color:#fff; font-size:1.45rem;
  box-shadow: 0 4px 14px oklch(0.49 0.103 155 / .32);
}
.hq-name { font-size:1.7rem; font-weight:700; color:var(--ink); line-height:1.1; }
.hq-name span { color:var(--brand); }
.hq-sub { font-size:.92rem; color:var(--muted); margin-top:.15rem; }
.hq-banner {
  margin:.9rem 0 1.3rem; padding:.7rem 1rem; border-radius:var(--radius-sm);
  background:var(--brand-tint); border:1px solid var(--border);
  color:var(--brand-700); font-size:.86rem; font-weight:500;
  display:flex; gap:.5rem; align-items:flex-start; line-height:1.6;
}

/* ── panel headings ───────────────────────────────────────────── */
.hq-h { font-size:.78rem; font-weight:700; letter-spacing:.02em; color:var(--muted);
        margin:0 0 .7rem; display:flex; align-items:center; gap:.45rem; }

/* ── case file ────────────────────────────────────────────────── */
.hq-card {
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius); padding:1.15rem 1.2rem; box-shadow:var(--shadow);
}
.hq-row { display:flex; justify-content:space-between; gap:1rem; padding:.6rem 0;
          border-top:1px solid var(--border); }
.hq-row:first-of-type { border-top:0; }
.hq-row .k { color:var(--muted); font-size:.86rem; }
.hq-row .v { color:var(--ink); font-weight:600; font-size:.92rem; text-align:left; }
.hq-pill { display:inline-block; padding:.16rem .6rem; border-radius:999px;
           background:var(--brand-tint); color:var(--brand-700);
           font-size:.82rem; font-weight:600; }
.hq-empty { color:var(--muted); font-size:.9rem; line-height:1.7; }
.hq-empty .dot { color:var(--brand); }

/* ── chat bubbles ─────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background:transparent; padding:.1rem 0; gap:.7rem;
  animation: hq-rise .42s var(--ease) both;
}
[data-testid="stChatMessageContent"] {
  direction:rtl; text-align:right; border-radius:var(--radius);
  padding:.5rem 1.05rem; box-shadow:var(--shadow); border:1px solid var(--border);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] {
  background:var(--brand-700); border-color:transparent;   /* darker: white text ≥4.5:1 */
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] * { color:#fff !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"])
  [data-testid="stChatMessageContent"] { background:var(--bg); }
[data-testid="stChatMessageContent"] h3 {
  font-size:1rem; color:var(--ink); margin:.7rem 0 .3rem; font-weight:700;
}
[data-testid="stChatMessageContent"] hr { margin:.9rem 0; border-color:var(--border); }

/* ── expanders: sources & flagged clauses ─────────────────────── */
[data-testid="stExpander"] { border:none; }
[data-testid="stExpander"] details {
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius-sm); margin-bottom:.55rem; overflow:hidden;
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease);
}
[data-testid="stExpander"] details:hover { border-color:var(--border-2); box-shadow:var(--shadow); }
[data-testid="stExpander"] summary { padding:.7rem .9rem; font-weight:600; color:var(--ink);
  font-size:.92rem; }
[data-testid="stExpander"] summary:hover { color:var(--brand); }
.hq-flag details { background:var(--warn-tint); border-color:oklch(0.86 0.06 78); }
.hq-flag summary { color:var(--warn-ink); }

/* ── chat input ───────────────────────────────────────────────── */
[data-testid="stChatInput"] { border-radius:var(--radius); border:1.5px solid var(--border-2);
  box-shadow:var(--shadow); background:var(--bg); }
[data-testid="stChatInput"]:focus-within { border-color:var(--brand); }
[data-testid="stChatInput"] textarea { font-size:1rem; color:var(--ink); }
[data-testid="stChatInput"] textarea::placeholder { color:var(--muted); opacity:1; }

/* ── buttons (sidebar + example chips) ────────────────────────── */
.stButton > button {
  border-radius:999px; border:1px solid var(--border-2); background:var(--bg);
  color:var(--ink); font-weight:500; font-size:.9rem; padding:.5rem 1rem;
  transition: all .18s var(--ease); text-align:right; line-height:1.6; height:auto;
}
.stButton > button:hover { border-color:var(--brand); color:var(--brand-700);
  background:var(--brand-tint); }
[data-testid="stSidebar"] { background:var(--surface-2); border-left:1px solid var(--border); }
[data-testid="stSidebar"] * { direction:rtl; }

/* ── scrollbar ────────────────────────────────────────────────── */
::-webkit-scrollbar { width:10px; height:10px; }
::-webkit-scrollbar-thumb { background:var(--border-2); border-radius:99px;
  border:2px solid var(--bg); }
::-webkit-scrollbar-thumb:hover { background:var(--muted); }

@keyframes hq-rise { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:none; } }
@media (prefers-reduced-motion: reduce) {
  [data-testid="stChatMessage"] { animation:none; }
  * { transition:none !important; }
}
</style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# State
# ──────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "last" not in st.session_state:
    st.session_state.last = {}


def ask(prompt: str):
    """Send one turn to the backend and store the result."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        resp = requests.post(
            f"{API_URL}/chat",
            json={"message": prompt, "profile": st.session_state.profile, "language": "ar"},
            timeout=120,
        ).json()
        reply = resp.get("reply", "(لا يوجد رد)")
        st.session_state.profile = resp.get("profile", st.session_state.profile)
        st.session_state.last = resp
        if resp.get("citations"):
            refs = "، ".join(c["article_ref"] for c in resp["citations"])
            reply += f"\n\n_المصادر: {refs}_"
    except Exception as e:
        reply = (f"تعذّر الوصول إلى الخادم ({e}). هل خدمة "
                 "`uvicorn app.main:app` تعمل؟")
        st.session_state.last = {}
    st.session_state.messages.append({"role": "assistant", "content": reply})


# ──────────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hq-top">
  <div class="hq-mark">⚖️</div>
  <div>
    <div class="hq-name">حقّي<span> · Haqqi</span></div>
    <div class="hq-sub">مساعدك لمعرفة حقوقك العمالية، مستنداً إلى نظام العمل السعودي.</div>
  </div>
</div>
<div class="hq-banner">
  <span>ℹ️</span>
  <span>هذه <b>معلومات قانونية</b> وليست استشارة قانونية. لكل حالة خصوصيتها — يُنصح بمراجعة محامٍ مرخّص.</span>
</div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="hq-h">⚙️ الإعدادات</div>', unsafe_allow_html=True)
    if st.button("↺ بدء محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.profile = {}
        st.session_state.last = {}
        st.rerun()
    st.markdown(
        '<p class="hq-empty" style="margin-top:1rem">صِف وضعك بالتفصيل، أو الصق بنود '
        'عقدك ليتم فحصها بنداً بنداً.</p>', unsafe_allow_html=True)

chat_col, case_col = st.columns([1.7, 1], gap="large")

# ──────────────────────────────────────────────────────────────────────────────
# Case file + findings (left in RTL)
# ──────────────────────────────────────────────────────────────────────────────
with case_col:
    profile = st.session_state.profile or {}
    shown = {k: v for k, v in profile.items() if k != "extra" and v not in (None, "", [])}
    rows = ""
    for k, v in shown.items():
        disp = STATUS_AR.get(v, v) if k == "employment_status" else v
        if k == "employment_status":
            disp = f'<span class="hq-pill">{disp}</span>'
        rows += f'<div class="hq-row"><span class="k">{LABELS.get(k, k)}</span>' \
                f'<span class="v">{disp}</span></div>'
    if not rows:
        rows = ('<p class="hq-empty"><span class="dot">●</span> '
                'يملأ المساعد هذا الملف تلقائياً كلما عرفت تفاصيل أكثر عن حالتك.</p>')
    st.markdown('<div class="hq-h">📂 ملف الحالة</div>'
                f'<div class="hq-card">{rows}</div>', unsafe_allow_html=True)

    last = st.session_state.last
    if last.get("flagged_clauses"):
        st.markdown('<div class="hq-h" style="margin-top:1.4rem">⚠️ بنود مخالفة</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="hq-flag">', unsafe_allow_html=True)
        for f in last["flagged_clauses"]:
            with st.expander(f.get("issue", "بند مخالف")):
                st.markdown(f"> {f.get('clause', '')}")
                st.caption(f"بحسب {f.get('citation', {}).get('article_ref', '')}")
        st.markdown('</div>', unsafe_allow_html=True)

    if last.get("citations"):
        st.markdown('<div class="hq-h" style="margin-top:1.4rem">📖 المصادر النظامية</div>',
                    unsafe_allow_html=True)
        for c in last["citations"]:
            with st.expander(c.get("article_ref", "مادة")):
                st.write(c.get("text", ""))
                meta = " · ".join(x for x in (c.get("source"), c.get("chapter")) if x)
                if meta:
                    st.caption(meta)

# ──────────────────────────────────────────────────────────────────────────────
# Chat (right in RTL)
# ──────────────────────────────────────────────────────────────────────────────
with chat_col:
    if not st.session_state.messages:
        st.markdown(
            '<div class="hq-card" style="margin-bottom:1rem">'
            '<div style="font-size:1.05rem;font-weight:700;color:var(--ink);margin-bottom:.3rem">'
            'كيف يمكنني مساعدتك؟ 👋</div>'
            '<p class="hq-empty">اكتب سؤالك في الأسفل، أو ابدأ بأحد الأمثلة:</p>'
            '</div>', unsafe_allow_html=True)
        for i, ex in enumerate(EXAMPLES):
            if st.button(ex, key=f"ex{i}", use_container_width=True):
                ask(ex)
                st.rerun()
    else:
        # User keeps Streamlit's default avatar so the message carries the
        # `stChatMessageAvatarUser` testid the CSS uses to tint the bubble green;
        # the assistant gets the brand ⚖️ mark.
        for m in st.session_state.messages:
            if m["role"] == "user":
                st.chat_message("user").markdown(m["content"])
            else:
                st.chat_message("assistant", avatar="⚖️").markdown(m["content"])

    if prompt := st.chat_input("صِف وضعك، أو الصق بنداً من العقد..."):
        ask(prompt)
        st.rerun()
